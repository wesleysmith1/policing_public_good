let civilianStealComponent = {
    components: {
    },
    props: {
        maps: Array,
        groupPlayerId: Number,
        investigationCount: Number,
        defendTokenTotal: Number,
        mapSize: Number,
        stealLocation: Number,
        activeSteal: Number,
        activeStealMaps: Object,
        fineNotification: String,
        stealTimeoutMilli: Number,
        stealTokenSlots: Number,
    },
    data: function () {
        return {
            location: null,
            locationx: 0,
            locationy: 0,
            timeout: null,
        }
    },
    mounted: function () {
        let that = this;
        let selector = '#location';
        Draggable.create(selector, {
            minimumMovement: .01,
            bounds: that.$refs.stealcontainer,
            onDragStart: function () {
                that.locationDragStart()
            },
            onDragEnd: function () {
                that.checkLocation(this)
            },
        });

    },
    methods: {
        cancelTimeout: function() {
            if (this.timeout)
                clearTimeout(this.timeout);
        },
        scheduleStealReset: function() {
            this.cancelTimeout();

            this.timeout = setTimeout(() => {
                let num = this.randomLocation();
                this.$emit('location-token-timeout', num);
            }, this.stealTimeoutMilli)
        },
        setStealLocation: function() {
            if (this.stealLocation === 1) {
                gsap.to('#location', 0, {x: 0, y: 0});
                return; // already starts in first steal location
            }

            let start = this.$refs['steallocation1'].getBoundingClientRect();
            let dest = this.$refs['steallocation' + this.stealLocation][0].getBoundingClientRect();

            gsap.to('#location', 0, {x: dest.x - start.x, y: dest.y - start.y});
        },
        locationDragStart: function () {
            this.cancelTimeout();

            // check the current location to see if we need to update api
            this.$emit('location-drag', {x: this.locationx, y: this.locationy, map: 0});
        },
        checkLocation: function (that) {

            if (that.hitTest(this.$refs.htarget, '10%')) {
                //location-centered
                for (let i in this.maps) {

                    // cannot steal from own map
                    if (this.maps[i]+1 === this.groupPlayerId)
                        continue

                    let id = parseInt(this.maps[i]) + 1;
                    if (that.hitTest(this.$refs['prop' + id], '.000001')) {
                        let map = this.$refs['prop' + id][0].getBoundingClientRect();
                        this.calculateLocation(map, id);
                        return;
                    }
                }
            }

            this.$emit('location-token-reset', this.randomLocation())
        },
        calculateLocation(map, map_id) {  // prop_id is more like the player_id
            let location = this.$refs.location.getBoundingClientRect();
            this.locationx = location.x - map.x + 2 - 1; // + radius - border
            this.locationy = location.y - map.y + 2 - 1;

            if (0 <= this.locationx &&
                this.locationx < this.mapSize &&
                0 <= this.locationy &&
                this.locationy < this.mapSize
            ) {
                this.scheduleStealReset();
                this.$emit('location-update', {x: this.locationx, y: this.locationy, map: map_id});
            } else {
                gsap.to('#location', 0, {x: 0, y: 0, ease: Back.easeOut});
            }
        },
        indicatorColor(map) {
            if (this.groupPlayerId === map) {
                return 'red'
            } else {
                return 'black'
            }
        },
        randomLocation: function () {
            return Math.floor(Math.random() * this.stealTokenSlots) + 1
        }
    },
    watch: {
        stealLocation: function () {
            this.$nextTick(() => {
                 this.setStealLocation();
            });
        }
    },
    template:
        `
      <div class="steal">
        <div class="game">
            <div id="steal-container" class="upper" ref="stealcontainer">
                <div class='title'>Civilian Maps</div> 
                    <div ref='htarget' class="maps-container">
                      <div v-for="map in maps" class="map-container">
                            <div
                                class="map"
                                v-bind:style="{ height: mapSize + 'px', width: mapSize + 'px', background: (groupPlayerId==map+1 ? (activeStealMaps[groupPlayerId] > 0 ? 'rgba(224,53,49,' + activeStealMaps[groupPlayerId] * .25 + ')' : 'darkgrey') : (map+1 == activeSteal ? 'rgba(81,179,100,.5)' : 'white'))}" 
                                v-bind:player-id="(map+1)" 
                                :id='"prop" + (map+1)' 
                                :ref='"prop" + (map+1)'>
                                <div id="home-fine-notification" v-if="groupPlayerId==map+1" style="text-align: center; font-size: 50px; padding-top: 40px;">
                                    {{fineNotification}}
                                </div>
                                <!-- svg indicator id format: map-player-->
                                <svg v-for="player_id in 5" :key="player_id" :id="'indicator-' + (map+1) + '-' + (player_id + 1)" class="indicator" width="16" height="16">
                                  <circle :id="'indicator-' + (map+1) + '-' + (player_id + 1) + '-circle'" cx="8" cy="8" r="4" :fill="indicatorColor(player_id+1)" />
                                </svg>
                            </div>
                            <div class="map-label">{{map+1 == groupPlayerId ? 'You' : 'Civilian ' + (map+1)}}</div>
                      </div>
                    </div>
                    <div class="token-container">
                        <div class="steal-locations-container">
                            <div class="steal-location" ref="steallocation1" id="steallocation1">
                                <svg id="location" height="21" width="21">
                                    <line x1="0" y1="0" x2="21" y2="21" class="steal-token-line"/>       
                                    <line x1="21" y1="0" x2="0" y2="21" class="steal-token-line"/>       
                                        
                                    <circle ref="location" cx="10.5" cy="10.5" r="2" fill="black" />
                                    Sorry, your browser does not support inline SVG.  
                                </svg> 
                            </div>
                            <div v-for="i in 19" class="steal-location" :ref='"steallocation" + (i+1)' :id='"steallocation" + (i+1)'>
                            </div>
                        </div>
                      <br>
                      <div>
                    </div>
              </div>
        </div>
      </div>
      </div>
      `

}