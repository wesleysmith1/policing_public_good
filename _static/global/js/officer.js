let officerGameComponent = {
    components: {
    },
    props: {
        maps: Array,
        initialDefendTokens: Array,
        officerIncome: Number,
        groupPlayerId: Number,
        investigationCount: Number,
        defendTokenTotal: Number,
        mapSize: Number,
        defendTokenSize: Number,
        probabilityReprimand: Number,
        reprimandAmount: Number,
    },
    data: function () {
        return {
            playerId: Number,
            locationx: String,
            locationy: String,
            map: String,
            activeCount: 0,
            mutableDefendTokens: Array,
            defendSlotStatuses: [],
        }
    },
    created: function () {
        this.mutableDefendTokens = this.initialDefendTokens;
        // sort slot data
        this.mutableDefendTokens.sort((a, b) => { return a.number - b.number });

        for (let i = 0; i < this.initialDefendTokens.length; i++)
            this.defendSlotStatuses.push(true);

        this.locationx = '';
        this.locationy = '';
        this.map = '';
    },
    mounted: function () {
        for (let i = 0; i < this.mutableDefendTokens.length; i++) {
            let that = this;
            let drag = Draggable.create("#unit" + (i+1), {
                minimumMovement: .01,
                bounds: this.$refs['officerGame'],
                onDragStart: function () {
                    let token = that.mutableDefendTokens[i]
                    that.tokenDragStart(this, token);
                    console.log(token)
                    // update map as dragging and adjust which tokens are active
                    if (token.map === 0) {
                        console.log("token dragged from start location", token.slot-1)
                        that.activeCount++;
                        that.defendSlotStatuses[token.slot-1] = false;
                        token.slot = 0;
                    }
                    token.map = -1;
                },
                onDragEnd: function () {
                    that.validateLocation(this, that.mutableDefendTokens[i])
                },
            });
        }
    },
    methods: {
        disableToken: function(id) {
            let selector = "#unit" + id;
            let dragToken = Draggable.get(selector);
            dragToken.disable();
            // gsap.to(selector, {background: 'red'});
            setTimeout(() => {
                dragToken.enable()
            }, 1000)
        },
        disableAllTokens() {
            // disable all tokens
            for (let i; i < this.mutableDefendTokens.length; i++) {
                Draggable.get('unit' + i).disable()
            }
        },
        tokenDragStart: function (that, token) {
            this.$emit('token-drag', token);
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

            console.log('hi')

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
            let slot = this.getSlot();

            let start = this.$refs['defendlocation' + (token.number)][0].getBoundingClientRect();
            let dest = this.$refs['defendlocation' + (slot)][0].getBoundingClientRect();
            gsap.to(tokenElm, 0, {x: dest.x - start.x, y: dest.y - start.y});

            // reset values slot status to occupied
            this.activeCount--;
            this.defendSlotStatuses[slot-1] = true;
            token.map = 0;
            token.slot = slot;

            this.$emit('defense-token-reset', token);

        },
        randomLocation: function() {
            // returns rand number 1-number of open defense token slots
            let count = Math.floor(Math.random() * this.activeCount) + 1;
            return count;
        }
    },
    template:
        `
        <div ref="officerGame">
            {{defendSlotStatuses}}
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
                    Civilian {{map+1}}
                    </div>
                </div>
            </div>
            <div class="token-container">
                <div style="margin: 10px">
                    <div class="title-small officer-info-container">
                        <div class="title-small data-row">
                            <div class="left">Amount earned per arrest: </div>
                            <div class="right green-txt bold-txt"><div class="number-right-align">{{officerIncome}}</div></div>
                        </div>
                    </div>
                    <div style="clear: both;"></div>
                </div>
                <div class="officer-units" v-bind:style="{ minHeight: defendTokenSize + 'px', }">
                    <div 
                        v-for="(unit, index) in mutableDefendTokens" 
                        :ref="'defendlocation'+(unit.number)"
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
                
                <div class="officer-info-container">
                    <div class="title-small data-row">
                        <div class="left">Amount lost per reprimand: </div>
                        <div class="right red-txt bold-txt"><div class="number-right-align">{{reprimandAmount}}</div></div>
                    </div>
                    <div style="clear: both;"></div>
                    <div class="title-small data-row">
                        <div class="left">Probability of reprimand: </div>
                        <div class="right red-txt bold-txt"><div class="number-right-align">{{probabilityReprimand}}%</div></div>
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