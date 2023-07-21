let totalQuantityChart = {
    components: {},
    props: {
        totalQuantity: Number,
        omega: Number,
    },
    data: function () {
        return {
            margin: {top: 30, right: 0, bottom: 25, left: 40},
            svg: null,
            height: null,
            width: null,
            yScale: null,
            xScale: null,
            bars: null,
            data: null,
        }
    },
    created: function() {

        this.width = 200 - this.margin.left - this.margin.right;
        this.height = 300 - this.margin.top - this.margin.bottom;

    },
    mounted: function () {

        this.chartInit();

    },
    methods: {
        chartInit: function() {
            this.svg = d3.select("svg#totalQuantity")
                .attr("width", this.width + this.margin.left + this.margin.right)
                .attr("height", this.height + this.margin.top + this.margin.bottom)
                .append("g")
                .attr("transform", "translate(" + this.margin.left + "," + this.margin.top + ")");
                
            this.yScale = d3.scaleLinear()
                .domain([0, this.omega * 4])
                .range([this.height, 0])

            this.data = [
                    {value: 0, label: 'Total Quantity', color: '#0F4392'},
                ]

            this.svg.append("g")
                .call(d3.axisLeft(this.yScale))
                .attr("class", "axisBlue")

            this.svg.append("text")
                .attr("x", (this.width / 2))
                .attr("y", 0 - (this.margin.top / 5))
                .attr("text-anchor", "middle")
                .attr("font-size", "35px")
                .text("")

            this.xScale = d3.scaleBand()
                .domain(this.data.map((d) => d.label))
                .range([0, this.width])
                .padding(.2)

            this.svg.append("g")
                .attr("transform", "translate( 0," + this.height + ")")
                .call(d3.axisBottom(this.xScale));

            this.bars = this.svg.selectAll("rect")
                .data(this.data)
                .enter().append("g")


            this.bars.append("rect")
                .attr("x", (d) => this.xScale(d.label))
                .attr("y", (d) => this.yScale(d.value))
                .attr("width", this.xScale.bandwidth())
                .attr("height", (d) => this.height - this.yScale(d.value))
                .attr("fill", (d) => d.color)

            this.bars.append("text")
                .text((d) => {return d.value})
                .attr("x", (d) => this.xScale(d.label))
                .attr("y", (d) => this.yScale(d.value) - 3)
                .attr("class", "label")
        },
        updateChart: function(value) {
            
            this.data[0].value = this.totalQuantity
            this.data[0].height  = this.yScale(this.totalQuantity)

            this.bars.selectAll("rect")
                .attr("height", (d) => this.height - this.yScale(d.value))
                .attr("y", (d) => this.yScale(d.value))

            this.bars.selectAll("text.label")
                .text((d) => {return d.value})
                .attr("x", (d) => this.xScale(d.label))
                .attr("y", (d) => d.height - 3)

        },
    },
    watch: {
        totalQuantity: function(newVal) {
            this.updateChart()
        },
    },
    computed: {

    },
    template:
        `
      <div>     
        <svg id="totalQuantity"></svg>
      </div>
      `
}
