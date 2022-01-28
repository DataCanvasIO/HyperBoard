

const OUTPUT_TYPE_LIB = 'lib'
const OUTPUT_TYPE_APP = 'app'




const baseConfig = {
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude:  /node_modules/,
                loader: 'babel-loader',
                options: {
                    presets: ['@babel/preset-env', '@babel/react'],
                    plugins: ['@babel/plugin-proposal-class-properties']
                }
            },
            {
                test: /\.css$/,
                use: [
                    'style-loader',
                    'css-loader'
                ]
            },
            {
                test: /\.(png|svg|jpg|gif)$/,
                use: [
                    'file-loader'
                ]
            }
        ]
    },
    resolve: {
        extensions: ['.js']
    },
    devServer:{
        writeToDisk:true,
        hot:false,
        inline: false,
    },
    mode: 'development'
};


const outputLibConfig = {

    entry: ['./src/index.js'],
    output: {
        path: __dirname + '/build',
        filename: 'experimentVis.js',
        libraryTarget: "commonjs", // commonjs, var
        library: 'experimentVis'
    },

};

const outputAppConfig = {
    entry: ['./src/app.js'],
    output: {
        path: __dirname + '/build',
        filename: 'experimentApp.js',
        libraryTarget: "commonjs", // commonjs, var
        library: 'experimentApp'
    }
};



module.exports = (env, argv) => {

    // try to merge app
    let config;
    console.info("env.outputType");
    console.info(env.outputType);

    const {outputType} = env;
    let outputType_;
    if (outputType !== undefined){
        outputType_ = outputType
    }else{
        outputType_ = OUTPUT_TYPE_LIB
    }
    // const outputType = env.outputType ? env.outputType !== undefined :  OUTPUT_TYPE_LIB

    console.info(outputType_);

    if(outputType_ === OUTPUT_TYPE_APP){
        config = {
            ...baseConfig,
            ...outputAppConfig
        }
    }else if(outputType_ === OUTPUT_TYPE_LIB){
        config = {
            ...baseConfig,
            ...outputLibConfig
        }
    }else {
        throw Error("Unknown output type " + outputType_);
    }

    console.info(JSON.stringify(config))
    return config;
}


