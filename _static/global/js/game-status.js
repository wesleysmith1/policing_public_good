let gameStatusComponent = {
    components: {
        'probability-bar-component': probabilityBarComponent,
        'grain-image-component': grainImageComponent,
    },
    props: {
        civiliansPerGroup: Number,
        balance: Number,
        balanceColor: String,
        stealNotification: String,
        interceptsCount: Number,
        finesCount: Number,
        reprimandsCount: Number,
        investigationCount: Number,
        defendTokenTotal: Number,
        isOfficer: Boolean,
        aMax: Number,
        beta: Number,
        reviewProbability: Number,
    },
    data: function () {
        return {
            probInnocent: [20,18,16,14,12,10,8,6,4],
            probCulprit: [20,26,32,38,44,50,56,62,68]
        }
    },
    mounted: function () {

    },
    methods: {
        randomLocation: function () {
            return null
        }
    },
    computed: {
        probabilityCulprit() {

            // todo do we need the amax thing anymore?
            return this.probCulprit[this.investigationCount]

            if (this.investigationCount > this.aMax)
                return 90;
            else {
                // let guilty = this.beta * (1/(this.civiliansPerGroup - 1) + ((this.civiliansPerGroup - 2) / (this.civiliansPerGroup - 1) * (this.investigationCount/this.aMax)))
                let guilty = this.beta + this.investigationCount * 12
                return guilty
                // return Math.round(guilty*10000) / 100
            }
        },
        probabilityInnocent() {
            let innocent = this.probInnocent[this.investigationCount]

            // calculate probability of officer reprimand because it depends on probability innocent
            if (this.isOfficer) {
                let probabilityReprimand = Math.round(this.reviewProbability * 3 * innocent * 10000) / 100
                this.$emit('update-probability-reprimand', probabilityReprimand)
            }
            return innocent
            // if (this.investigationCount > this.aMax)
            //     return 0;
            // else {
            //     // let innocent = this.beta * ((1/(this.civiliansPerGroup -1) - (1/(this.civiliansPerGroup -1)) * (this.investigationCount/this.aMax)))

            //     // let innocent = this.beta - this.investigationCount * 3
            //     let innocent = this.probInnocent[this.investigationCount]

            //     // calculate probability of officer reprimand because it depends on probability innocent
            //     if (this.isOfficer) {
            //         let probabilityReprimand = Math.round(this.reviewProbability * 3 * innocent * 10000) / 100
            //         this.$emit('update-probability-reprimand', probabilityReprimand)
            //     }
            //     return innocent
            //     // return Math.round(innocent*10000) / 100
            // }
        },
    },
    template:
        `
            <div class="game-status-container">
                <div class="balance-container">
                    <div class="balance-label">Balance (<grain-image-component :size=20></grain-image-component>)</div>
                    <div class="balance" :style="{ color: balanceColor }"> {{balance.toFixed(0)}}</div>
            
                    <div class="notification-label">
                        <div class="steal-notification">{{stealNotification}}</div>
                    </div>
            
                    <br>
                    <br>
                </div>
                <div class="probability-container">
                    <div class="title">
                        Probability {{ isOfficer ? 'you fine' : 'fined' }}
                    </div>
                    <div class="inner">
                        <probability-bar-component
                                :label="isOfficer ? 'An innocent' : 'If you are innocent'"
                                :percent="isOfficer ? probabilityInnocent * 3 : probabilityInnocent">
                        </probability-bar-component>
                        <br>
                        <probability-bar-component
                                :label="isOfficer ? 'The culprit' : 'If you are the culprit'"
                                :percent=probabilityCulprit
                        ></probability-bar-component>
                        <br>
                        <div class="title-small data-row">
                            <div class="left">Officer tokens on investigate:</div>
                            <div class="right bold-txt"><div class="number-right-align">{{investigationCount}}/{{defendTokenTotal}}</div></div>
                        </div>
                        <div style="clear: both;"></div>
                        <br>
                    </div>
                </div>
                <div class="officer-history">
                    <div class="title">
                        Officer history
                    </div>
                    <div class="count-container">
                        <div class="title-small data-row">
                            <div class="left"># Intercepts: </div>
                            <div class="right"><strong>{{ interceptsCount }}</strong></div>
                        </div>
                        <div style="clear: both"></div>
                        <div class="title-small data-row">
                            <div class="left"># Fines: </div>
                            <div class="right"><strong>{{ finesCount }}</strong></div>
                        </div>
                        <div style="clear: both"></div>
                        <div class="title-small data-row">
                            <div class="left"># Reprimands: </div>
                            <div class="right"><strong>{{ reprimandsCount }}</strong></div>
                        </div>
                    </div>
                </div>
            </div>
        `

}