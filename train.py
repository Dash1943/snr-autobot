on_space      = spaces.Discrete(3)
            self.step_idx          = window

        def reset(self):
            self.step_idx = self.window
            return self._get_obs()
import argparse
import pandas as pd
import gym
import numpy as np
from stable_baselines3 import PPO
from gym import spaces

def make_env(df, window=50):
    class TradeEnv(gym.Env):
        def __init__(self):
            super().__init__()
            self.df = df.reset_index(drop=True)
            self.window = window
            # 特徵
            self.df['ema20'] = self.df['close'].ewm(span=20).mean()
            self.df['ema60'] = self.df['close'].ewm(span=60).mean()
            self.df['rsi14'] = self.df['close'].rolling(14).apply(lambda x: (x.diff()>0).sum()/14*100)
            self.df['atr14'] = (self.df['high']-self.df['low']).rolling(14).mean()
            self.df['resist']  = self.df['high'].rolling(window).max()
            self.df['support'] = self.df['low'].rolling(window).min()
            self.observation_space = spaces.Box(-np.inf, np.inf, shape=(7,), dtype=np.float32)
            self.acti
        def _get_obs(self):
            row = self.df.iloc[self.step_idx]
            return np.array([
                row['close'], row['ema20'], row['ema60'],
                row['rsi14'], row['atr14'],
                (row['close']-row['support'])/row['support'],
                (row['resist']-row['close'])/row['close'],
            ], dtype=np.float32)

        def step(self, action):
            # 獎勵計算與邏輯可依需求擴充
            self.step_idx += 1
            done = self.step_idx >= len(self.df)-1
            reward = 0
            return self._get_obs(), reward, done, {}

    return TradeEnv()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', required=True)
    parser.add_argument('--out_dir', default='models/ppo_wave_bot_snr')
    args = parser.parse_args()

    df = pd.read_csv(args.data, parse_dates=['datetime'])
    env = make_env(df)
    model = PPO('MlpPolicy', env, verbose=1)
    model.learn(total_timesteps=200_000)
    model.save(args.out_dir)
