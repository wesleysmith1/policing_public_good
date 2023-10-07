let yourCostChart = {
    components: {},
    props: {
        omega: Number,
        totalQuantity: Number,
        idInGroup: Number,
        yourCost: Number,
    },
    data: function () {
        return {
            marginCost: {top: 30, right: 0, bottom: 25, left: 60},
            svg: null,
            height: null,
            width: null,
            costYScale: null,
            costXScale: null,
            bars: null,
            costData: null,
        }
    },
    created: function() {

        this.width = 200 - this.marginCost.left - this.marginCost.right;
        this.height = 300 - this.marginCost.top - this.marginCost.bottom;

    },
    mounted: function () {

        this.costBarInit();

    },
    methods: {
        costBarInit: function() {

            this.svg = d3.select("svg#costBar2")
                .attr("width", this.width + this.marginCost.left + this.marginCost.right)
                .attr("height", this.height + this.marginCost.top + this.marginCost.bottom)
                .append("g")
                .attr("transform", "translate(" + this.marginCost.left + "," + this.marginCost.top + ")");
                
            this.costYScale = d3.scaleLinear()
                .domain([0, 4000])
                .range([this.height, 0])

            this.costData = [
                    {value: 0, label: 'Your Cost', color: '#FF4949', scale: this.costYScale},
                ]

            this.svg.append("g")
                .call(d3.axisLeft(this.costYScale))
                .attr("class", "axisBlue")

            this.svg.append("text")
                .attr("x", (this.width / 2))
                .attr("y", 0 - (this.marginCost.top / 5))
                .attr("text-anchor", "middle")
                .attr("font-size", "35px")
                .text("")

            this.costXScale = d3.scaleBand()
                .domain(this.costData.map((d) => d.label))
                .range([0, this.width])
                .padding(.2)

            this.svg.append("g")
                .attr("transform", "translate( 0," + this.height + ")")
                .attr("transform", "translate(0," + this.costYScale(0) + ")")
                .call(d3.axisBottom(this.costXScale));

            this.costBar = this.svg.selectAll("rect")
                .data(this.costData)
                .enter().append("g")

            this.costBar.append("rect")
                .attr("x", (d) => this.costXScale(d.label))
                .attr("y", (d) => d.scale(Math.max(0, d.value)))
                .attr("width", this.costXScale.bandwidth())
                .attr("height", (d) => Math.abs(d.scale(d.value) - d.scale(0)))
                .attr("fill", (d) => d.color)

            this.costBar.append("text")
                .text(Math.round(this.yourCost))
                .attr("x", (d) => this.costXScale(d.label))
                .attr("y", (d) => d.scale(Math.max(0, d.value)) - 3)
                .attr("class", "label")
        },
        updateCostChart: function(value) {
            
            this.costData[0].value = this.yourCost

            this.costBar.selectAll("rect")
            .attr("height", function(d) {return Math.abs(d.scale(d.value) - d.scale(0))})
            .attr("y", (d) => d.scale(d.value))
            .attr("fill", "green")

            this.costBar.selectAll("text.label")
                .text(Math.round(this.yourCost))
                .attr("x", (d) => this.costXScale(d.label))
                .attr("y", (d) => d.scale(d.value) - 3)
                .attr("class", "label")
        },
    },
    watch: {
        yourCost: function(newVal) {
            this.updateCostChart()
        },
    },
    computed: {

    },
    template:
        `
      <div>     
        <svg id="costBar2"></svg>
      </div>
      `
}
