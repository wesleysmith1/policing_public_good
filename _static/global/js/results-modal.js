let resultsModalComponent = {
    components: {
        'grain-image-component': grainImageComponent,
    },
    props: {
        resultsObject: Object,
        isOfficer: Boolean,
        income: Number, // needed to calculate officer breakdown
    },
    data: function() {
        return {

        }
    },
    methods: {
        openModal: function() {
            this.$refs.myModal.style.display = 'block';
        }
    },
    template:
        `
        <div ref="myModal" class="modal">

          <div class="modal-content results-modal">
            
            <div v-if="resultsObject" class="modal-content results-modal">
                <h4 style="text-align: center;">{{ resultsObject.title }}</h4>
                                
                <div class="list-group" style="width: 450px; margin: auto;">
                    
                    <div v-if="resultsObject.balance != null" class="list-group-item">
                        <div style="display: flex; justify-content: space-between;">
                            <div>Balance <grain-image-component :size=20></grain-image-component></div>
                            <div>{{ resultsObject.balance.toFixed(0) }}</div>
                        </div>
                    </div>      
    
                </div>
                <br>
                
                <template v-if="isOfficer">
                    <p style="text-align: center; margin-top: 15px;">Breakdown</p>
                    <div class="list-group" style="width: 450px; margin: auto;">
                        
                        <div v-if="resultsObject.fines != null" class="list-group-item list-group-item-primary">
                            <div style="display: flex; justify-content: space-between;">
                                <div>Amount earned ( <grain-image-component :size=20></grain-image-component>{{resultsObject.officer_bonus}} per civilian fined ):  </div>
                                <div><grain-image-component :size=20></grain-image-component>{{ resultsObject.fines * income }}</div>
                            </div>
                        </div>
                        <div v-if="resultsObject.reprimands != null" class="list-group-item list-group-item-primary">
                            <div style="display: flex; justify-content: space-between;">
                                <div>Amount lost ( <grain-image-component :size=20></grain-image-component>{{resultsObject.officer_reprimand_amount}} per reprimand ):</div>
                                <div><grain-image-component :size=20></grain-image-component>{{ resultsObject.reprimands * resultsObject.officer_reprimand_amount * -1 }}</div>
                            </div>
                        </div>   
                        
                    </div>
                </template>

            </div>
            
            
          </div>
        
        </div>
        `
}