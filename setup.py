from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aquestalk",
    version="1.0.0",
    author="KaenbiyouRin",
    description="Python wrapper for AquesTalk speech synthesis engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KaenbiyouRin/aquestalk",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Development Status :: 4 - Beta",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    install_requires=["numpy>=1.18.0", "soundfile>=0.10.0"],
    extras_require={
        "dev": ["pytest>=6.0", "twine>=3.0"],
        "full": ["aqkanji2koe>=0.1.0"],  # 依赖之前的文本转音素库
    },
    project_urls={
        "Bug Reports": "https://github.com/KaenbiyouRin/aquestalk/issues",
        "Source": "https://github.com/KaenbiyouRin/aquestalk",
    },
)