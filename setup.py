# setup.py
from setuptools import find_packages, setup

def install_requirements():
    with open("requirements.txt") as f:
        return [
            req.strip()
            for req in f.readlines()
            if req.strip() and not req.startswith("#")
        ]

setup(
    name="ai-medical-chatbot",
    version="0.0.1",
    description="AI-powered medical chatbot using LangChain, FastAPI, and FAISS",
    author="Ikram Naoui",
    packages=find_packages(),  
    install_requires=install_requirements(),
)
