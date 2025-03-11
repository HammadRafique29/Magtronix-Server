import React, { useEffect, useRef, useState } from "react";

const CircularTimer = ({ duration }: { duration: number }) => {
  const [countdown, setCountdown] = useState<number>(duration);
  const countdownRef = useRef<number>(duration); // Reference to sync state immediately

  const radius = 100; // Circle radius
  const strokeWidth = 22; // Thickness of the circle
  const circumference = 2 * Math.PI * radius; // Total circumference of the circle

  const progress = ((duration - countdownRef.current) / duration) * circumference;

  useEffect(() => {
    const interval = setInterval(() => {
      setCountdown((prev) => {
        if (prev > 0) {
          countdownRef.current = prev - 1; // Update ref synchronously
          return prev - 1;
        }
        clearInterval(interval); // Clear interval when countdown reaches 0
        return 0;
      });
    }, 1000); // Set interval to 1 second

    return () => clearInterval(interval); // Cleanup interval on unmount
  }, []);

  // Calculate stroke-dashoffset for progress
  

  return (
    <div
      id="countdown"
      style={{
        position: "relative",
        margin: "auto",
        height: `${radius * 2 + strokeWidth * 2}px`,
        width: `${radius * 2 + strokeWidth * 2}px`,
        textAlign: "center",
      }}
    >
      {/* Countdown Number */}
      <div
        id="countdown-number"
        style={{
          color: "white",
          fontSize: "70px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          height: "100%",
          backgroundColor: "#00000070",
          borderRadius: 1000
        }}
      >
        {Math.floor(countdown)}
      </div>

      {/* Circular Progress */}
      <svg
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: `${radius * 2 + strokeWidth * 2}px`,
          height: `${radius * 2 + strokeWidth * 2}px`,
          transform: "rotateY(-180deg) rotateZ(-90deg)",
          // borderRadius: "50px"
        }}
      >
        <circle
          r={radius}
          cx={radius + strokeWidth}
          cy={radius + strokeWidth}
          style={{
            strokeDasharray: `${circumference}px`,
            strokeDashoffset: `${circumference - progress}px`,
            strokeLinecap: "round",
            strokeWidth: `${strokeWidth}px`,
            stroke: "white",
            fill: "none",
            transition: "stroke-dashoffset 1s linear",
          }}
        />
      </svg>
    </div>
  );
};

export default CircularTimer;
