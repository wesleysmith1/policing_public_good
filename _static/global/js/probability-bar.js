let probabilityBarComponent = {
    props: {
        label: String,
        percent: Number,
    },
    data: function () {
        return {
            defenseTokens: []
        }
    },
    template:
        `
        <div>
            <div class="title-small data-row">
                <div class="left">{{ label }}:</div>
                <div class="right bold-txt"><div class="number-right-align">{{percent}}%</div></div>
            </div>
            <div style="clear: both;"></div>
            <div class='bar'>
                <div class="innocent" :style="{'width':(percent+'%')}">
                </div>
            </div>
        </div>
        `
}