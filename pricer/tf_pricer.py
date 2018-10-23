import numpy as np
import tensorflow as tf
import scipy.stats as stats
import matplotlib.pyplot as plt
import datetime
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

def timer(func):
    def wrapper(*args, **kwargs):
        t1 = datetime.datetime.now()
        func(*args, **kwargs)
        t2 = datetime.datetime.now()
        print( "Function %s Time it took to run the function: %s" % (func.__name__, str(t2 - t1)) )
    return wrapper

def blackScholes_py(S_0, strike, time_to_expiry, implied_vol, riskfree_rate):
    S = S_0
    K = strike
    dt = time_to_expiry
    sigma = implied_vol
    r = riskfree_rate
    Phi = stats.norm.cdf
    d_1 = (np.log(S_0 / K) + (r+sigma**2/2)*dt) / (sigma*np.sqrt(dt))
    d_2 = d_1 - sigma*np.sqrt(dt)
    return S*Phi(d_1) - K*np.exp(-r*dt)*Phi(d_2)

def blackScholes_tf_pricer(enable_greeks = True):
    # Build the static computational graph
    S = tf.placeholder(tf.float32)
    K = tf.placeholder(tf.float32)
    dt = tf.placeholder(tf.float32)
    sigma = tf.placeholder(tf.float32)
    r = tf.placeholder(tf.float32)
    Phi = tf.distributions.Normal(0.,1.).cdf
    d_1 = (tf.log(S / K) + (r+sigma**2/2)*dt) / (sigma*tf.sqrt(dt))
    d_2 = d_1 - sigma*tf.sqrt(dt)
    npv =  S*Phi(d_1) - K*tf.exp(-r*dt)*Phi(d_2)
    target_calc = [npv]
    if enable_greeks:
        greeks = tf.gradients(npv, [S, sigma, r, K, dt])
        dS_2ndOrder = tf.gradients(greeks[0], [S, sigma, r, K, dt]) 
        # Calculate mixed 2nd order greeks for S (esp. gamma, vanna) and sigma (esp. volga)
        dsigma_2ndOrder = tf.gradients(greeks[1], [S, sigma, r, K, dt])
        dr_2ndOrder = tf.gradients(greeks[2], [S, sigma, r, K, dt]) 
        dK_2ndOrder = tf.gradients(greeks[3], [S, sigma, r, K, dt]) 
        dT_2ndOrder = tf.gradients(greeks[4], [S, sigma, r, K, dt])
        target_calc += [greeks, dS_2ndOrder, dsigma_2ndOrder, dr_2ndOrder, dK_2ndOrder, dT_2ndOrder]
    
    # Function to feed in the input and calculate the computational graph
    def execute_graph(S_0, strike, time_to_expiry, implied_vol, riskfree_rate):
        with tf.Session() as sess:
            res = sess.run(target_calc, 
                           {
                               S: S_0,
                               K : strike,
                               r : riskfree_rate,
                               sigma: implied_vol,
                               dt: time_to_expiry})
        return res
    return execute_graph

def create_tf_graph_for_simulate_paths():
    S = tf.placeholder(tf.float32)
    K = tf.placeholder(tf.float32)
    dt = tf.placeholder(tf.float32)
    T = tf.placeholder(tf.float32)
    sigma = tf.placeholder(tf.float32)
    r = tf.placeholder(tf.float32)
    dw = tf.placeholder(tf.float32)
    S_T = S * tf.cumprod(tf.exp((r-sigma**2/2)*dt+sigma*tf.sqrt(dt)*dw), axis=1)
    return (S, K, dt, T, sigma, r, dw, S_T)

def make_path_simulator():
    (S,K, dt, T, sigma, r, dw, S_T) = create_tf_graph_for_simulate_paths()
    def paths(S_0, strike, time_to_expiry, implied_vol, riskfree_rate, seed, n_sims, obs):
        if seed != 0:
            np.random.seed(seed)
        stdnorm_random_variates = np.random.randn(n_sims, obs)
        with tf.Session() as sess:
            timedelta = time_to_expiry / stdnorm_random_variates.shape[1]
            res = sess.run(S_T, 
                           {
                               S: S_0,
                               K : strike,
                               r : riskfree_rate,
                               sigma: implied_vol,
                               dt : timedelta,
                               T: time_to_expiry,
                               dw : stdnorm_random_variates
                         })
            return res
    return paths
 
def create_plain_vanilla_mc_tf_pricer(enable_greeks = True):
    (S,K, dt, T, sigma, r, dw, S_T) = create_tf_graph_for_simulate_paths()
    payout = tf.maximum(S_T[:,-1] - K, 0)
    npv = tf.exp(-r*T) * tf.reduce_mean(payout)
    target_calc = [npv]
    if enable_greeks:
        greeks = tf.gradients(npv, [S, sigma, r, K, T])
        target_calc += [greeks]
    def pricer(S_0, strike, time_to_expiry, implied_vol, riskfree_rate, seed, n_sims):
        if seed != 0:
            np.random.seed(seed)
        stdnorm_random_variates = np.random.randn(n_sims, 1)
        with tf.Session() as sess:
            timedelta = time_to_expiry / stdnorm_random_variates.shape[1]
            res = sess.run(target_calc, 
                           {
                               S: S_0,
                               K : strike,
                               r : riskfree_rate,
                               sigma: implied_vol,
                               dt : timedelta,
                               T: time_to_expiry,
                               dw : stdnorm_random_variates
                         })
            return res
    return pricer

def create_geometric_asian_mc_tf_pricer(enable_greeks = True):
    (S,K, dt, T, sigma, r, dw, S_T) = create_tf_graph_for_simulate_paths()
    A = tf.pow(tf.reduce_prod(S_T, axis=1),dt/T)
    payout = tf.maximum(A - K, 0)
    npv = tf.exp(-r*T) * tf.reduce_mean(payout)
    target_calc = [npv]
    if enable_greeks:
        greeks = tf.gradients(npv, [S, sigma, r, K, T])
        target_calc += [greeks]
    def pricer(S_0, strike, time_to_expiry, implied_vol, riskfree_rate, seed, n_sims, obs):
        if seed != 0:
            np.random.seed(seed)
        stdnorm_random_variates = np.random.randn(n_sims, obs)
        with tf.Session() as sess:
            timedelta = time_to_expiry / obs
            res = sess.run(target_calc, 
                           {
                               S: S_0,
                               K : strike,
                               r : riskfree_rate,
                               sigma: implied_vol,
                               dt : timedelta,
                               T: time_to_expiry,
                               dw : stdnorm_random_variates
                         })
            return res
    return pricer
    
def main():
    path_simulator = make_path_simulator()
    paths = path_simulator(100, 110.,  2, 0.2, 0.03, 1312, 10, 400)
    plt.figure(figsize=(8,5))
    _= plt.plot(np.transpose(paths))
    _ = plt.title('Simulated Path')
    _ = plt.ylabel('Price')
    _ = plt.xlabel('TimeStep') 

main()