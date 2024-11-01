import gym
import numpy as np
from collections import deque
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import random
import matplotlib.pyplot as plt

# Create the environment (CartPole or MountainCar)
env = gym.make("CartPole-v1")  # or "MountainCar-v0"
state_size = env.observation_space.shape[0]
action_size = env.action_space.n

# Parameters
episodes = 20  # Reduced number of episodes
learning_rate = 0.001
discount_factor = 0.95
epsilon = 1.0
epsilon_decay = 0.995
epsilon_min = 0.01
batch_size = 64
memory = deque(maxlen=2000)

# Build Q-Network
model = Sequential([
    Dense(24, input_dim=state_size, activation='relu'),
    Dense(24, activation='relu'),
    Dense(action_size, activation='linear')
])
model.compile(loss='mse', optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate))

# Experience replay function
def replay():
    global epsilon
    if len(memory) < batch_size:
        return
    minibatch = random.sample(memory, batch_size)
    for state, action, reward, next_state, done in minibatch:
        target = reward
        if not done:
            target += discount_factor * np.amax(model.predict(next_state)[0])
        target_f = model.predict(state)
        target_f[0][action] = target
        model.fit(state, target_f, epochs=1, verbose=0)
    if epsilon > epsilon_min:
        epsilon *= epsilon_decay

# List to hold scores for plotting
scores = []

# Train the agent
for e in range(episodes):
    state = env.reset()
    state = np.reshape(state, [1, state_size])
    score = 0  # Initialize score for this episode
    for time in range(100):  # Reduced max steps
        # Choose action (epsilon-greedy strategy)
        if np.random.rand() <= epsilon:
            action = random.randrange(action_size)
        else:
            action = np.argmax(model.predict(state)[0])

        # Perform the action
        next_state, reward, done, _ = env.step(action)
        next_state = np.reshape(next_state, [1, state_size])

        # Store experience in memory
        memory.append((state, action, reward, next_state, done))

        state = next_state
        score += reward  # Accumulate score

        # Print intermediate scores to keep output flowing
        if time % 10 == 0:  # Print every 10 steps
            print(f"Episode: {e+1}/{episodes}, Step: {time}, Current Score: {score}")

        if done:
            print(f"Episode: {e+1}/{episodes}, Final Score: {score}, Epsilon: {epsilon:.2f}")
            break

    scores.append(score)  # Store the score for this episode
    if e % 5 == 0:  # Learn every 5 episodes
        replay()

# Plotting scores
plt.plot(scores)
plt.title('Scores Over Episodes')
plt.xlabel('Episodes')
plt.ylabel('Score')
plt.grid()
plt.show()

env.close()
