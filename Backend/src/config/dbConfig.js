import mongoose from 'mongoose';
import serverConfig from './serverConfig.js';
async function connectDB(){
    try{
        await mongoose.connect(serverConfig.DB_URL);
        console.log("Successfully connected to the mongodb server...");
    } catch(error){
        console.log("Not able to connect mongodb server...");
        console.log(error)
    }
}
export default connectDB;