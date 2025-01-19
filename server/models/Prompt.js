const mongoose = require("mongoose")

const PromptSchema = new mongoose.Schema({
    template: {
        type: String,
        required: true
    },
    variables: {
        type: [String],
        default: []
    },
    username: {
        type: String,
        default: "root",
        ref: 'User'
    }
})

module.exports = mongoose.model('Prompt', PromptSchema)