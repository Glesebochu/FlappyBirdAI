# 🐦 Flappy Bird AI - NEAT Evolution Edition

Welcome to the **Flappy Bird AI** project! 🎮 This repository brings together **Python**, **Pygame**, and **NEAT (NeuroEvolution of Augmenting Topologies)** to create an AI that learns to play Flappy Bird—by evolving smarter strategies generation after generation. 🌟

## 🚀 Features
- **AI-Driven Gameplay** 🧠: Uses the **NEAT algorithm** to evolve neural networks that make smarter decisions.
- **Wind Effects 🌬️**: Adds complexity with random wind forces to challenge the AI.
- **High Jumps 🚀**: Enables adaptive high jumps to counter environmental effects.
- **Dynamic Visualization 📊**: Displays AI learning progress with fitness graphs using **matplotlib**.

## 📂 Project Structure
```
FlappyBirdAI/
├── images/               # Game assets (background, bird, walls, wind)
├── venv/                 # Python virtual environment
├── ConfigFile.txt        # NEAT configuration
├── main.py               # Main game and AI logic
└── winner.pkl            # Saved best genome (after training)
```

## 🛠️ Setup Instructions

1. **Clone the Repository** 🖥️:
```bash
$ git clone https://github.com/yourusername/FlappyBirdAI.git
$ cd FlappyBirdAI
```

2. **Set Up Virtual Environment** 🐍:
```bash
$ python -m venv venv
$ source venv/bin/activate   # On MacOS/Linux
$ .\venv\Scripts\activate   # On Windows
```

3. **Install Dependencies** 📦:
```bash
$ pip install -r requirements.txt
```

4. **Run the AI** 🤖:
```bash
$ python main.py
```

5. **Choose a Mode** 🎮:
- **Train the AI:** Press **T**
- **Play manually:** Press **P**
- **Watch the best genome:** Press **B**

6. **Exit Training Anytime** 🛑:
Press **Q** to save progress and quit.

## 📈 Tracking Progress
- AI performance is displayed with real-time **generation numbers** and **fitness scores**.
- View performance graphs after training to analyze trends in learning.

## 🧪 Configuration Highlights
- **Population Size:** 200 (Ensures genetic diversity)
- **Mutation Rates:**
  - **Weight Mutations:** 80% for exploration.
  - **Replace Weights:** 10% for drastic changes.
- **Activation Function:** `tanh` for smooth outputs (-1 to 1).
- **Fitness Threshold:** Stops training once fitness exceeds **10,000**.

## 🏆 Saving and Using the Best Genome
- The best genome is saved in **winner.pkl**.
- Reuse the best AI by selecting **Play Best Genome** mode.

## 🤔 Troubleshooting
- **Missing Assets?** Ensure the **images/** folder has all required game sprites.
- **Virtual Environment Not Found?** Activate the virtual environment before running commands.
- **No Best Genome Found?** Train the AI first before selecting **B** mode.

## 📜 License
This project is licensed under the **Apache 2.0 License**. Feel free to use, modify, and distribute it under the terms of this license!

---

Contributions are welcome! 🛠️ Submit pull requests or issues to help improve the AI. 🎉


