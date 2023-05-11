let grainImageComponent = {
    props: {
        size: Number,
    },
    data: function() {
        return {

        }
    },
    methods: {

    },
    template:
        `
          <img src="https://i.imgur.com/BQXgE3F.png" alt="grain" :style="{ height: size + 'px' }">
        `
}