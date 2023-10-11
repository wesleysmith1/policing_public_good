let startModalComponent = {
    components: {
        'grain-image-component': grainImageComponent,
    },
    props: {
        startObject: Object,
        isOfficer: Boolean,
        groupPlayerId: Number,
        mechanismObject: Object,
        roundNumber: Number,
    },
    methods: {
        open: function() {
            this.$refs.smodal.style.display = 'block';
        },
        close: function() {
            this.$refs.smodal.style.display = 'none';
        },
        incomeStyle(id) {
            console.log('here is the index')
            if (this.groupPlayerId == id) {
                return {fontWeight: 'bold'}
            } else {
                return {}
            }
        }

    },
    computed: {
        officerItem() {
            return this.isOfficer ? {fontWeight: 'bold'} : {}
        },
        civilianItem() {
            return this.isOfficer ? {} : {fontWeight: 'bold'}
        },
        sortedIds() {
            let sortedIds = Object.keys(this.startObject.civilian_incomes);
            sortedIds.sort((a,b) => { return this.startObject.civilian_incomes[a] - this.startObject.civilian_incomes[b] });
            return sortedIds
        }
    },
    template:
        `
        <div ref="smodal" class="modal">
            <!--Modal content-->
            <div class="modal-content start-modal">
                <div class="start-modal-content">
                    <div v-if="mechanismObject && roundNumber > 2">
                        <h4 style="text-align:center;">Market Over</h4>
                        <p style="text-align: center;">Summary</p>
                        <div v-if="mechanismObject.participant" class="list-group" style="width: 450px; margin: auto;">
                            <div v-if="mechanismObject.your_quantity != null && !isOfficer" class="list-group-item list-group-item-primary">
                                <div style="display: flex; justify-content: space-between;">
                                    <div><strong>Your quantity:</strong></div>
                                    <div><strong>{{mechanismObject.your_quantity}}</strong></div>
                                </div>
                            </div>
                            <div v-if="mechanismObject.your_cost != null && !isOfficer" class="list-group-item list-group-item-primary">
                                <div style="display: flex; justify-content: space-between;">
                                    <div><strong>Your cost:</strong></div>
                                    <div><strong>{{ mechanismObject.your_cost.toFixed(0) }}</strong></div>
                                </div>
                            </div>
                            <div v-if="mechanismObject.total_quantity != null" class="list-group-item list-group-item-primary">
                                <div style="display: flex; justify-content: space-between;">
                                    <div><strong>Total quantity:</strong></div>
                                    <div><strong>{{ mechanismObject.total_quantity.toFixed(0) }}</strong></div>
                                </div>
                            </div> 
                        </div>
                        <br>
                        <div class="list-group" style="width: 450px; margin: auto;">
                            <div v-if="mechanismObject.starting_points != null && !isOfficer" class="list-group-item list-group-item-secondary">
                                <div style="display: flex; justify-content: space-between;">
                                    <div><strong>Your starting balance:</strong></div>
                                    <div><strong>{{ mechanismObject.starting_points}}</strong></div>
                                </div>
                            </div>
                            <div v-if="mechanismObject.participant_rebate & !mechanismObject.treatment == 'OGL' && !isOfficer" class="list-group-item list-group-item-secondary">
                                <div style="display: flex; justify-content: space-between;">
                                    <div><strong>Your rebate:</strong></div>
                                    <div><strong>{{ mechanismObject.participant_rebate }}</strong></div>
                                </div>
                            </div>
                            <div v-if="mechanismObject.your_cost != null && !isOfficer" class="list-group-item list-group-item-secondary">
                                <div>
                                    <div v-if="mechanismObject.participant" style="display: flex; justify-content: space-between;">
                                        <div><strong>Your cost:</strong></div>
                                        <div><strong>{{ mechanismObject.your_cost.toFixed(0) }}</strong></div>
                                    </div>
                                    <div v-else style="display: flex; justify-content: space-between;">
                                        <div><strong>Your tax:</strong></div>
                                        <div><strong>{{ mechanismObject.nonparticipant_tax.toFixed(0) }}</strong></div>
                                    </div>
                                    
                                </div>
                            </div>
                            <div v-if="mechanismObject.total_quantity != null && !isOfficer" class="list-group-item list-group-item-secondary">
                                <div style="display: flex; justify-content: space-between;">
                                    <div><strong>Total quantity:</strong></div>
                                    <div><strong>{{ mechanismObject.total_quantity.toFixed(0) }}</strong></div>
                                </div>
                            </div>
                            <div v-if="mechanismObject.balance != null" class="list-group-item list-group-item-secondary">
                                <div style="display: flex; justify-content: space-between;">
                                    <div><strong>Current balance:</strong></div>
                                    <div><strong>{{ mechanismObject.balance.toFixed(0) }}</strong></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <br>

                    <div v-if="startObject">
                        <h4 style="text-align:center;">Round information</h4>
                        <br>
                        <!--<p style="text-align: center;">Token summary</p>-->
                                        
                        <div class="list-group" style="width: 450px; margin: auto;">
                             <div class="list-group-item">
                                <div style="display: flex; justify-content: space-between;">
                                    <div>Officer earnings per civilian fine </div>
                                    <div :style=officerItem><grain-image-component :size=20></grain-image-component>{{startObject.officer_bonus}}</div>
                                </div>
                            </div>
                            <div class="list-group-item">
                                <div style="display: flex; justify-content: space-between;">
                                    <div>Officer reprimand </div>
                                    <div :style="officerItem"><grain-image-component :size=20></grain-image-component>{{ startObject.officer_reprimand }}</div>
                                </div>
                            </div>
                            <div class="list-group-item">
                                <div style="display: flex; justify-content: space-between;">
                                    <div>Civilian fine</div>
                                    <div :style="civilianItem"><grain-image-component :size=20></grain-image-component>{{ startObject.civilian_fine }}</div>
                                </div>
                            </div>
                            <div class="list-group-item">
                                <div style="display: flex; justify-content: space-between;">
                                    <div>Civilian steal rate </div>
                                    <div :style="civilianItem"><grain-image-component :size=20></grain-image-component>{{ startObject.steal_rate }}</div>
                                </div>
                            </div>
                            <div class="list-group-item">
                                <div style="display: flex; justify-content: space-between;">
                                    <div>Civilian harvest rates <grain-image-component :size=20></grain-image-component></div>
                                    <div>
                                        <span v-for="id in sortedIds" v-bind:style="incomeStyle(id)">
                                            {{ startObject.civilian_incomes[id] }} <span> </span>
                                        </span>
                                    </div>
                                </div>
                            </div>        
                        </div>
                    </div>
                </div>
            </div>
        </div>
        `
}