const mongoose = require('mongoose')

const connectDB = async () => {
    console.log("Connecting to MongoDB");
    try {
        const conn = await mongoose.connect(process.env.MONGO_URI)
        console.log(`MongoDB Connected: ${conn.connection.host}`.cyan.underline.bold);
        
    } catch (err) {
        console.log(`Error Occured: ${err}`.red.underline.bold);
        
    }
}

module.exports = connectDB