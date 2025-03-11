import { AbsoluteFill, Sequence } from 'remotion';
import React from 'react';
import { Animated, Scale } from 'remotion-animated';

type NumberDesignProps = {
	number: number;
};

export const VideoNumber: React.FC<NumberDesignProps> = ({ number }) => {
	console.log(number);
	return (
		<AbsoluteFill>
			<div className="circle-container">
				<div className="circle">
					<Sequence from={4} style={{position: "absolute", display: "flex", justifyContent: "center", alignItems: "center"}}>
					<Animated
						animations={[Scale({ initial: 2.5, by: 1.5 })]}
						style={{
						display: "flex",
						justifyContent: "center",
						alignItems: "center",
						fontSize: "2rem", // Ensure font size is dynamic
						}}
					>
						{number}
					</Animated>
					</Sequence>
				</div>
				<div className="line left-line"></div>
				<div className="line right-line"></div>
			</div>

			<style>
				{`
					.circle-container {
						position: absolute;
						//top: 0px; /* 10px from the top */
						left: 50%;
						transform: translateX(-50%);
						display: flex;
						justify-content: center;
						align-items: center;
						z-index: 999; /* Above other elements */
						// background-color: red;
					}

					.circle {
						background-color: #2121216b;
						color: white;
						font-size: 32px;
						font-weight: bold;
						width: 120px;
						height: 120px;
						border-radius: 50%;
						display: flex;
						justify-content: center;
						align-items: center;
                        font-size: 40pt;
						z-index: 2;
					}

					.line {
						position: absolute;
						top: 50%;
						width: 250px;
						height: 15px;
						background-color: #2121216b;
						transform: translateY(-50%);
						z-index: 1;
                        border-radius: 10px;
					}

					.left-line {
						left: -250px;
					}

					.right-line {
						right: -250px;
					}
				`}
			</style>
		</AbsoluteFill>
	);
};

