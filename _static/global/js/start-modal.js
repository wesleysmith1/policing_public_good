let startModalComponent = {
    components: {
        'grain-image-component': grainImageComponent,
    },
    props: {
        startObject: Object,
        isOfficer: Boolean,
        groupPlayerId: Number,
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