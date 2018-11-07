// returns a gaussian random function with the given mean and stdev.
function gaussian(mean, stdev) {
    var y2;
    var use_last = false;
    return function() {
        var y1;
        if(use_last) {
           y1 = y2;
           use_last = false;
        }
        else {
            var x1, x2, w;
            do {
                 x1 = 2.0 * Math.random() - 1.0;
                 x2 = 2.0 * Math.random() - 1.0;
                 w  = x1 * x1 + x2 * x2;               
            } while( w >= 1.0 || w == 0);
            w = Math.sqrt(-2.0 * Math.log(w) / w);
            y1 = x1 * w;
            y2 = x2 * w;
            use_last = true;
       }

       var retval = mean + stdev * y1;
       return retval;
   }
}

function BlackScholes(PutCallFlag, S, X, T, r, v) {

    var d1, d2;
    d1 = (Math.log(S / X) + (r + v * v / 2.0) * T) / (v * Math.sqrt(T));
    d2 = d1 - v * Math.sqrt(T);


    if (PutCallFlag== "c")
        return S * CND(d1)-X * Math.exp(-r * T) * CND(d2);
    else
        return X * Math.exp(-r * T) * CND(-d2) - S * CND(-d1);

}

/* The cummulative Normal distribution function: */

function CND(x){

    var a1, a2, a3, a4 ,a5, k ;

    a1 = 0.31938153, a2 =-0.356563782, a3 = 1.781477937, a4= -1.821255978 , a5= 1.330274429;

    if(x<0.0)
        return 1-CND(-x);
    else
        k = 1.0 / (1.0 + 0.2316419 * x);
    return 1.0 - Math.exp(-x * x / 2.0)/ Math.sqrt(2*Math.PI) * k
        * (a1 + k * (-0.356563782 + k * (1.781477937 + k * (-1.821255978 + k * 1.330274429)))) ;

}

function BsmCallMc(S_t, K, r, vol, T) {
    // Number of time steps for simulation
	var n_steps = Math.floor(T * 252)
	// Time interval
	var dt = T / n_steps
	// Number of simulations
    var N = 100000
    // Zero array to store values (often faster than appending)
    var S = Array(n_steps).fill().map(() => Array(N).fill(S_t))
    var standard = gaussian(0, 1);

    for (var t=0; t<n_steps-1; t++) {
        for (var u=0; u<N; u++) {
            S[t+1][u] = S[t][u] * Math.exp((r - 0.5 * Math.pow(vol, 2)) * dt + (vol * Math.sqrt(dt) * standard()))
        }
    }
    
    S.map(x=>
        console.log(x[N-1])
    )
    var C = Math.exp(-r * T) * 1 / N * Math.max( S.map(x=>x[N-1]-K), 0 )
    return C
}

var S_0 = 100
var K = 110
var T = 0.5
var r = 0.03
var vol = 0.5

var C = BsmCallMc(S_0, K, r, vol, T)

console.log("Strike price: " + K.toFixed(2))
console.log("Monte Carlo Option Value Estimate: " + C.toFixed(2))