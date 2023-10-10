let officerGameComponent = {
    components: {
        'grain-image-component': grainImageComponent,
    },
    props: {
        maps: Array,
        initialDefendTokens: Array,
        officerIncome: Number,
        mapSize: Number,
        defendTokenSize: Number,
        probabilityReprimand: Number,
        reprimandAmount: Number,
        defendPauseDuration: Number,
        playerBalances: Object
    },
    data: function () {
        return {
            locationx: String,
            locationy: String,
            map: String,
            activeCount: 0,
            mutableDefendTokens: [],
            defendSlotStatuses: [],
            inactiveDefendTokenNums: [],
            overflowDefendTokens: [],
            showOverflow: true,
            minimumMovement: .01,
            defendTokenDisplayMax: 8,
        }
    },
    created: function () {
        // this.mutableDefendTokens = this.initialDefendTokens;
        // // sort slot data
        // this.mutableDefendTokens.sort((a, b) => { return a.number - b.number });

        // for (let i = 0; i < this.initialDefendTokens.length; i++)
        //     this.defendSlotStatuses.push(true);

        // this.locationx = '';
        // this.locationy = '';
        // this.map = '';
        this.initialDefendTokens.sort((a, b) => { return a.number - b.number });

        this.initialDefendTokens.forEach(t => {
            if (t.number > this.defendTokenDisplayMax) {
                this.overflowDefendTokens.push(t)
                this.inactiveDefendTokenNums.push(t.number)
            } else {
                this.mutableDefendTokens.push(t)
                this.defendSlotStatuses.push(true)
            }
        });
    },
    mounted: function () {
        this.mutableDefendTokens.forEach(t => this.createDraggable(this, t))
        this.overflowDefendTokens.forEach(t => this.createDraggable(this, t))
        // for (let i = 0; i < this.mutableDefendTokens.length; i++) {
        //     let that = this;
        //     let drag = Draggable.create("#unit" + (i+1), {
        //         minimumMovement: .01,
        //         bounds: this.$refs['officerGame'],
        //         onDragStart: function () {
        //             let token = that.mutableDefendTokens[i]
        //             that.tokenDragStart(this, token);
        //             // update map as dragging and adjust which tokens are active
        //             if (token.map === 0) {
        //                 that.activeCount++;
        //                 that.defendSlotStatuses[token.slot-1] = false;
        //                 token.slot = 0;
        //             }
        //             token.map = -1;
        //         },
        //         onDragEnd: function () {
        //             that.validateLocation(this, that.mutableDefendTokens[i])
        //         },
        //     });
        // }
    },
    methods: {
        showToken: function(number) {
            // display overflow token
            this.$refs['unit' + number][0].style.display = 'block';
        },
        hideToken: function(number) {
            // display overflow token
            this.$refs['unit' + number][0].style.display = 'none';
        },
        moveTokenToOverflow: function(tokenElm, token) {
            // move token to overflow container
            let overflowRef = this.$refs['overflowcontainer'];
            let overflowRect = overflowRef.getBoundingClientRect();

            // slot reflects where token was first loaded on the page
            let slotRef = this.$refs['slot' + token.number][0];
            let slotRect = slotRef.getBoundingClientRect();

            gsap.to(tokenElm, 0, {x: slotRect.x - overflowRect.x, y: slotRect.y - overflowRect.y});
        },
        getTokenByNum: function(number) {
            // search for token in Token and Overflow Token lists
            let found = null;
            if (number > this.defendTokenDisplayMax) {
                found = this.overflowDefendTokens.find(t => t.number == number);
            } else {
                found = this.mutableDefendTokens.find(t => t.number == number);
            }
            if (!found) {
                console.error('unable to find token by number');
            }
            return found
        },
        createDraggable: function(that, token) {
            Draggable.create("#unit" + token.number, {
                minimumMovement: this.minimumMovement,
                onDragStart: function () {
                    that.tokenDragStart(this, token);
                },
                onDragEnd: function () {
                    that.tokenDragEnd(this, token);
                },
            });
        },
        disableToken: function(id) {
            let selector = "#unit" + id;
            let dragToken = Draggable.get(selector);
            dragToken.disable();
            setTimeout(() => {
                dragToken.enable()
            }, 1000)
        },
        disableAllTokens: function() {
            for (let i = 1; i <= this.mutableDefendTokens.length; i++) {
                let token = Draggable.get("#unit" + (i));
                token.disable();
            }
            for (let i = 1; i <= this.overflowDefendTokens.length; i++) {
                let token = Draggable.get("#unit" + (i));
                token.disable();
            }
        },
        tokenDragStart: function (that, token) {
            // token dragged from token start slots
            if (token.map === 0) {
                this.updateSlotStatus(token.slot, false)
                token.slot = 0;
            }
            token.map = -1;
            this.$emit('token-drag', token);
        },
        tokenDragEnd: function (that, token) {
            // check where token landed

            // maps
            let mapHit = false
            for (let i in this.maps) {
                let id = parseInt(this.maps[i]) + 1;

                if (that.hitTest(this.$refs['map' + id], '.000001%')) { // todo: this is perhaps too accurate?
                    token.map = id;
                    let map = this.$refs['map' + id][0].getBoundingClientRect();
                    this.updateLocation(map, that, token);
                    mapHit = true
                    // break out of loop
                    break
                }
            }

            // investigation
            if (that.hitTest(this.$refs.investigationcontainer, '100%')) {
                token.map = 11;
                this.investigationUpdate(token)
                this.checkStoredTokens()
            } else if (!mapHit) {
                this.resetDefendToken(that.target, token)
            }

            // check if overflow has tokens
            this.checkStoredTokens()

        },
        checkStoredTokens: function() {
            // if overflow has tokens and slots are available display slot
            if (this.checkSlotAvailability() && this.inactiveDefendTokenNums.length) {
                let tokenNum = this.inactiveDefendTokenNums.pop()

                if (!tokenNum) {
                    console.error('tokenNum not found')
                    return
                }
                // todo: make this cleaner
                let slot = this.pickSlot();
                let tokenElm = this.$refs['unit' + tokenNum][0]
                let token = this.getTokenByNum(tokenNum);
                this.moveTokenToSlot(tokenElm, token, slot);

                // show token
                this.showToken(tokenNum)
                // update slot
                this.updateSlotStatus(slot, true)
            }
        },
        checkSlotAvailability: function() {
            // return true if any slots are available]
            let i = 0;
            for (i; i < this.defendSlotStatuses.length; i++) {
                if (!this.defendSlotStatuses[i])
                    return true
            }
            return false
        },
        investigationUpdate: function(token) {
            this.$emit('investigation-update', token);
        },
        updateLocation: function(map, unitContext, token) {
            let unit = unitContext.target.getBoundingClientRect();
            token.x = unit.x - map.x - 1;
            token.y = unit.y - map.y - 1;
            // disable token
            this.disableToken(token.number);
            // update api with unit location
            this.updateDefendToken(token);
        },
        updateSlotStatus: function(slot, status) {
            if (slot < 1) {
                console.error('slot must be greater than 0');
            }

            this.defendSlotStatuses[slot-1] = status
        },
        pickSlot: function() {
            // returns randomly selected slot number from open slots

            // calculate where to send
            let nthSlot = this.nthOpenSlot();
            let i = 0;
            let counter = 0
            for(i; i<this.defendSlotStatuses.length; i++) {
                if (!this.defendSlotStatuses[i])
                    counter++
                // did we reach the randomly selected slot?
                if (counter === nthSlot)
                    return i+1;
            }
            console.error('error pickSlot returned -1')
            return -1;
        },
        moveTokenToSlot: function(tokenElm, token, slot) {

            let slotRef = this.$refs['slot' + slot][0];
            let startRef = this.$refs['slot' + token.number][0];

            let startRect = startRef.getBoundingClientRect();
            let slotRect = slotRef.getBoundingClientRect();

            gsap.to(tokenElm, 0, {x: slotRect.x - startRect.x, y: slotRect.y - startRect.y});
            this.updateSlotStatus(slot, true)

            token.map = 0;
            token.slot = slot;

        },
        nthOpenSlot: function() {
            // return random number 1 to number of available slots
            let availableSlotCount = 0;
            let i = 0;
            for (i; i < this.defendSlotStatuses.length; i++) {
                if (!this.defendSlotStatuses[i]) {
                    availableSlotCount++;
                }
            }

            // returns rand number 1-number of open defense token slots
            if (!availableSlotCount) {
                console.error('random location cannot be found because there are no available slots');
            }
            return Math.floor(Math.random() * availableSlotCount) + 1;
        },
        validateLocation: function (that, token) {
            if (that.hitTest(this.$refs.officerGame, '100%')) {
                for (let i in this.maps) {
                    let id = parseInt(this.maps[i]) + 1;

                    if (that.hitTest(this.$refs['map' + id], '.000001%')) {
                        this.map = id;
                        token.map = id;
                        let map = this.$refs['map' + id][0].getBoundingClientRect();
                        this.calculateLocation(map, that, token);
                        return;
                    }
                }

                if (that.hitTest(this.$refs.investigationcontainer, '100%')) {
                    token.map = 11;
                    this.$emit('investigation-update', token);
                    return;
                }
            }

            this.resetDefendToken(that.target, token)
        },
        calculateLocation: function(map, unitContext, token) {
            let unit = unitContext.target.getBoundingClientRect();
            this.locationy = unit.y - map.y - 1;
            this.locationx = unit.x - map.x - 1;
            token.x = this.locationx;
            token.y = this.locationy;
            this.disableToken(token.number);
            // update api with unit location
            this.updateDefendToken(token);
        },
        updateDefendToken: function(token) {
            this.$emit('token-update', token);
        },
        getSlot: function() {
            // calculate where to send
            let randSlot = this.randomLocation();

            let i = 0;
            let count = 0;
            for(i; i<this.defendSlotStatuses.length; i++) {
                if (!this.defendSlotStatuses[i])
                    count++;
                else
                    continue;

                // did we reach the randth element?
                if (count === randSlot)
                    return i+1;
            }
            return -1;
        },
        resetDefendToken: function(tokenElm, token) {
            // if slot is available send to slot else send to overflow, update backend
            let slot = this.pickSlot();

            console.log('slot in resetDefendToken', slot);

            // token must be sent to overflow
            if (slot == -1) {
                console.error('slot wrong');
                // send to overflow
                this.moveTokenToOverflow(tokenElm, token);
                this.hideToken(token.number);
                this.inactiveDefendTokenNums.push(token.number);
                return;
            }

            this.moveTokenToSlot(tokenElm, token, slot)

            this.$emit('defense-token-reset', token);

        },
        randomLocation: function() {
            // returns rand number 1-number of open defense token slots
            let count = Math.floor(Math.random() * this.activeCount) + 1;
            return count;
        },
    },
    template:
        `
          <div ref="officerGame">
              <div class="upper">      
                <div class='title'>Civilian Maps</div> 
                <div class="maps-container">
                    <div v-for="map in maps" v-bind:player-id="(map+1)" :id='"map" + (map+1)' :ref='"map" + (map+1)' class="map-container">
                      <div class="map other" :id='"map" + (map+1)' :ref='"map" + (map+1)' v-bind:style="{ height: mapSize + 'px', width: mapSize + 'px' }">
                            <div v-for="player_id in 5" class="intersection-label" :id="'intersection-label-' + (map+1) + '-' + (player_id + 1)" >
                                -1
                            </div>
                            <svg v-for="player_id in maps" :key="player_id" :id="'indicator-' + (map+1) + '-' + (player_id + 1)" class="indicator" width="16" height="16">
                                <circle :id="'indicator-' + (map+1) + '-' + (player_id + 1) + '-circle'" cx="8" cy="8" r="4" fill="black" />
                            </svg>
                      </div>
                      <div class="map-label">
                        {{'Civilian ' + (map+1) + ' '}} 
                    </div>
                    </div>
                </div>
                <div class="token-container">
                    <div style="margin: 10px">
                        <div class="title-small officer-info-container">
                            <div class="title-small data-row">
                                <div class="left">Amount earned per fine: </div>
                                <div class="right green-txt bold-txt"><div class="number-right-align"><grain-image-component :size=35 color="green"></grain-image-component>{{officerIncome}}</div></div>
                            </div>
                        </div>
                        <div style="clear: both;"></div>
                    </div>
                    <div style="font-size: ">Plus {{ inactiveDefendTokenNums.length }} additional Tokens</div>
                    <div class="officer-units" v-bind:style="{ minHeight: defendTokenSize + 'px', }">
                        <div 
                            v-for="(unit, index) in mutableDefendTokens" 
                            :ref="'slot'+(unit.number)"
                            :id="'defendslot' + (unit.number)" 
                            class="defend-location" 
                            v-bind:style="{ height: defendTokenSize + 'px', width: defendTokenSize + 'px' }"
                        >
                            <div 
                                :id="'unit' + unit.number" 
                                :ref='"unit" + unit.number'
                                class="officer-unit" 
                                v-bind:style="{ height: defendTokenSize + 'px', width: defendTokenSize + 'px' }"
                            >
                            </div>
                        </div>
                    </div>
                    <div ref="overflowcontainer" id="overflow-container" v-bind:style="{ marginTop: '-' + (defendTokenSize + 5) + 'px', marginLeft: 5 + 'px', minHeight: defendTokenSize + 'px'}">
                        <div
                            v-for="(unit, index) in overflowDefendTokens"
                            class="overflow-slot"
                            v-bind:style="{ height: defendTokenSize + 'px', width: defendTokenSize + 'px' }"
                            :ref="'slot'+(unit.number)"
                        >
                            <div
                                :id="'unit' + unit.number"
                                :ref='"unit" + unit.number'
                                class="officer-unit"
                                v-bind:style="{ height: defendTokenSize + 'px', width: defendTokenSize + 'px' }"
                                v-show="false"
                            >
                            </div>
                        </div>
                    </div>
                    <div class="officer-info-container">
                        <div class="title-small data-row">
                            <div class="left">Amount lost per reprimand: </div>
                            <div class="right red-txt bold-txt"><div class="number-right-align"><grain-image-component :size=35 style="color: red"></grain-image-component>{{reprimandAmount}}</div></div>
                        </div>
                        <div style="clear: both;"></div>
                        <div class="title-small data-row">
                            <div class="left">Probability of reprimand per fine: </div>
                            <div class="right red-txt bold-txt"><div class="number-right-align">{{(probabilityReprimand / 100).toFixed(2)}}%</div></div>
                        </div>
                    </div>
                </div>
                <div class="investigation-data-container">
                    <div class="title">Investigation Map</div>
                    <div id="officer-investigation-container" ref='investigationcontainer' v-bind:style="{ height: mapSize + 'px' }"></div>
                </div>
              </div>
          </div>
      `
}