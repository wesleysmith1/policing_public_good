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
            probInnocent: [
                [25.00,23.33,21.67,20.00,18.33,16.67,15.00,13.33,11.67,10.00,8.33,6.67,5.00,3.33,1.67,0],
                [75.00,70.00,65.00,60.00,55.00,50.00,45.00,40.00,35.00,30.00,25.00,20.00,15.00,10.00,5.00,0],
            ],
            probCulprit: [25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100]
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
            return this.investigationCount > 15 ? 100 : this.probCulprit[this.investigationCount]

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
            let innocent = this.investigationCount > 15 ? 0 : this.probInnocent[0][this.investigationCount]

            // calculate probability of officer reprimand because it depends on probability innocent
            if (this.isOfficer) {
                let probabilityReprimand = Math.round(this.reviewProbability * 3 * innocent * 10000) / 100
                this.$emit('update-probability-reprimand', probabilityReprimand)

                return this.probInnocent[1][this.investigationCount]
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
                                :percent="isOfficer ? probabilityInnocent: probabilityInnocent">
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