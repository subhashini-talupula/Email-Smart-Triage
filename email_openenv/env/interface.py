from fastapi import FastAPI
from pydantic import BaseModel
from env.environment import EmailEnv

app = FastAPI()
env = EmailEnv("easy")

class ActionInput(BaseModel):
    label: str

@app.post("/reset")
def reset():
    obs = env.reset()
    return {"email": obs.email.dict(), "step_count": obs.step_count}

@app.post("/step")
def step(action: ActionInput):
    obs, reward, done, _ = env.step(action)
    return {
        "observation": obs.email.dict(),
        "reward": reward.score,
        "done": done,
        "reason": reward.reason
    }