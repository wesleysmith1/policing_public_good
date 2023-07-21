let oglComponent = {
    components: {
        'total-quantity-chart': totalQuantityChart,
        'your-quantity-chart': yourQuantityChart,
        'your-cost-chart': yourCostChart,
    },
    props: {
        paymentMax: Number,
        provisionalTotals: Object,
        totalQuantity: Number,
        playerQuantity: Number,
        playerId: Number,
        idInGroup: Number,
        bigN: Number,
        gamma: Number,
        omega: Number,
        constants: Object,
        groupQuantities: Object,
        startingBalance: Number,
        plus: Number,
        minus: Number,
        yourCost: Number,
        utility: Number,
    },
    data: function () {
        return {
            numberTokens: 0,
            paymentOptions: null,
            provisional: {},
            formInputNum: null,
            inputPlaceholder: 0,
            data: {},
            costData: {},
            svg: null,
            width: null,
            height: null,
            yScale: null,
            costYScale: null,
            costXScale: null,
            xScale: null,
            bars: null,
            mechanism: "OGL",
        }
    },
    created: function() {
        this.numberTokens = this.playerQuantity
        this.inputPlaceholder = this.playerQuantity
        // Decimal.set({ precision: 8 })
        this.paymentOptions = this.paymentMax * 2;

    },
    mounted: function () {
    },
    methods: {
        preventKeyboardInput: function(e) {
            if (e.key == 'ArrowRight' | e.key == 'ArrowLeft' | e.key == 'ArrowUp' | e.key == 'ArrowDown') {
                e.preventDefault()
            }
        },
        playerCost: function() {
            return 100 * Math.random()
        },
        jsonCopy: function(src) {
            return JSON.parse(JSON.stringify(src));
        },
        incrementTotal: function() {
            if (this.numberTokens >= this.omega) {
                return;
            }
            this.numberTokens = parseInt(this.numberTokens)+ 1
            this.inputPlaceholder = this.numberTokens
            this.inputChange()
        },
        decrementTotal: function() {
            if (this.numberTokens <= 0) {
                return;
            }
            this.numberTokens -= 1
            this.inputPlaceholder = this.numberTokens
            this.inputChange()
        },
        validateOmega: function() {
            return (this.formInputNum <= this.omega && this.formInputNum >= 0)
        },
        handleFormSubmission: function() {
            // remove focus from form
            this.$refs.glinput.blur()

            if (Number.isInteger(this.formInputNum) && this.validateOmega()) {
                this.updatePlaceholder()

                this.inputChange()
            } else {
                this.formInputNum = null
            }
        },
        updatePlaceholder: function() {
            this.numberTokens = this.formInputNum
            this.inputPlaceholder = this.formInputNum
            this.formInputNum = null;
        },
        inputChange: function() {
            this.$emit('update', this.numberTokens);
        },
        arrIntSum: function(arr) {
            if (!arr) {
                console.error('arrIntSum received empty value')
                return -999
            }

            if (!Array.isArray(arr))
                arr = Object.values(arr)

            let sum =  arr.reduce(function(a,b){
                return a + b
            }, 0);
            return Math.round(sum);
        },
        rangeUpdate: function() {
            // range slider was moved.
            this.inputChange()
        },
        isNumber: function(evt) {
            evt = (evt) ? evt : window.evt;
            var charCode = (evt.which) ? evt.which : evt.keyCode;
            if ((charCode < 48 || charCode > 57) && charCode !== 45) {
                evt.preventDefault();
            } else {
                return true;
            }
        },
    },
    watch: {
        playerQuantity: function(newVal) {
            this.inputPlaceholder = this.playerQuantity

        },
        totalQuantity: function(newVal) {
        },
        groupQuantities: {
            deep: true,
            handler: function(newVal, oldVal){
               // this handler allows the child component to get updated quantities
            }
        },
    },
    computed: {

    },
    template:
        `
      <div>     

        <h2 style="text-align: center">Your points: {{startingBalance}}</h2>

        <div style="display: flex; justify-content: space-around">
            <your-quantity-chart :player-quantity="playerQuantity" :omega="omega"></your-quantity-chart>
            <total-quantity-chart :total-quantity="totalQuantity" :omega="omega"></total-quantity-chart>
            <your-cost-chart :total-quantity="totalQuantity" :omega="omega" :yourCost="yourCost" :idInGroup="idInGroup"></your-cost-chart>
        </div>

        <br>
        <h4 style="text-align: center;">Your payoff: {{utility.toFixed(0)}}</h4>
        <br>
      
        <div class="slidecontainer">
            <input type="range" min="0" :max=omega value="0" class="slider" id="barRange" v-model="numberTokens" @change="rangeUpdate">
            <p>Value: <span id="demo">{{numberTokens}}</span></p>
        </div>

        <div>
        <h3 style="text-align: center;">Provisional</h3>
        </div>
        
        <div class="" style="display: flex; justify-content: space-between; align-items: flex-end;">
            <div style="min-width: 200px; display: flex; flex-direction: column; margin-bottom: 16px;">
                <button v-show="playerQuantity > 0" @click="decrementTotal(1)" type="button" class="btn btn-primary">Update Quantity (-1)</button>
            </div>
            <div style="margin-bottom: 16px;">
                <form style="display: flex;" @submit.prevent="handleFormSubmission()">
                  <button type="submit" class="btn btn-primary">Update Quantity</button>
                  <div class="form-group" style="max-width: 250px;">
                    <input ref="glinput" type="number" step="1" class="form-control" v-on:keyup.enter="handleFormSubmission()" @keypress="isNumber($event)" :placeholder="inputPlaceholder" style="max-width: 250px;" v-model.number="formInputNum">
                  </div>
                </form>
            </div>
            
            <div style="min-width: 200px; display: flex; flex-direction: column; margin-bottom: 16px;">
                <button v-show="playerQuantity < omega" @click="incrementTotal(1)" type="button" class="btn btn-primary">Update Quantity (+1)</button>
            </div>
        </div>
      
        <div class="" style="display: flex; justify-content: space-between;">
            <div style="min-width: 200px;">
                <div v-show="playerQuantity > 0">
                    <div class="list-group">
                        <div class="list-group-item list-group-item-secondary">
                            <div style="display: flex; justify-content: space-between;">
                                <div>Your quantity:</div>
                                <div>{{playerQuantity - 1}}</div>
                            </div>
                        </div>
                        <div class="list-group-item list-group-item-secondary">
                            <div style="display: flex; justify-content: space-between;">
                                <div>Total quantity:</div>
                                <div>{{ totalQuantity - 1 }}</div>
                            </div>
                        </div>
                        <div class="list-group-item list-group-item-secondary">
                            <div style="display: flex; justify-content: space-between;">
                                <div>Your cost:</div>
                                <div>{{ minus ? minus.toFixed(0) : minus }}</div>
                            </div>
                        </div>              
                    </div>
                </div>
            </div>
        
        
            <div style="min-width: 350px;">
                <div>
                    <div class="list-group">
                        <div class="list-group-item list-group-item-primary">
                            <div style="display: flex; justify-content: space-between;">
                                <div><b>Your quantity:</b></div>
                                <div><b>{{playerQuantity}}</b></div>
                            </div>
                        </div>
                        <div class="list-group-item list-group-item-primary">
                            <div style="display: flex; justify-content: space-between;">
                                <div>Total quantity:</div>
                                <div>{{ totalQuantity }}</div>
                            </div>
                        </div>
                        <div class="list-group-item list-group-item-primary">
                            <div style="display: flex; justify-content: space-between;">
                                <div><b>Your cost:</b></div>
                                <div><b>{{ yourCost.toFixed(0)}}</b></div>
                            </div>
                        </div>                
                    </div>
                </div>
            </div>
            
            <div style="min-width: 200px;">
                <div v-show="playerQuantity < omega">            
                    <div class="list-group">
                        <div class="list-group-item list-group-item-secondary">
                            <div style="display: flex; justify-content: space-between;">
                                <div>Your quantity:</div>
                                <div>{{ playerQuantity + 1 }}</div>
                            </div>
                        </div>
                        <div class="list-group-item list-group-item-secondary">
                            <div style="display: flex; justify-content: space-between;">
                                <div>Total quantity:</div>
                                <div>{{ totalQuantity + 1 }}</div>
                            </div>
                        </div>
                        <div class="list-group-item list-group-item-secondary">
                            <div style="display: flex; justify-content: space-between;">
                                <div>Your cost:</div>
                                <div>{{ plus ? plus.toFixed(0): plus }}</div>
                            </div>
                        </div>             
                    </div> 
                </div>
            </div>
        </div>
      </div>
      `
}
