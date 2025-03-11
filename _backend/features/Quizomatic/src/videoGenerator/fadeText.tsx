
// "use client";

// import { motion, Variants } from "framer-motion";
// import { useMemo } from "react";

// type FadeTextProps = {
//   className?: string;
//   direction?: "up" | "down" | "left" | "right";
//   framerProps?: Variants;
//   text: string;
// };

// export function FadeText({
//   direction = "up",
//   className,
//   framerProps = {
//     hidden: { opacity: 0 },
//     show: { opacity: 1, transition: { type: "spring" } },
//   },
//   text,
// }: FadeTextProps) {
//   const directionOffset = useMemo(() => {
//     const map = { up: 10, down: -10, left: -10, right: 10 };
//     return map[direction];
//   }, [direction]);

//   const axis = direction === "up" || direction === "down" ? "y" : "x";

//   const FADE_ANIMATION_VARIANTS = useMemo(() => {
//     const { hidden, show, ...rest } = framerProps as {
//       [name: string]: { [name: string]: number; opacity: number };
//     };

//     return {
//       ...rest,
//       hidden: {
//         ...(hidden ?? {}),
//         opacity: hidden?.opacity ?? 0,
//         [axis]: hidden?.[axis] ?? directionOffset,
//       },
//       show: {
//         ...(show ?? {}),
//         opacity: show?.opacity ?? 1,
//         [axis]: show?.[axis] ?? 0,
//       },
//     };
//   }, [directionOffset, axis, framerProps]);

//   return (
//     <motion.div
//       style={{ display: "inline-block", width: "auto" }} // Ensure it spans the full width
//       initial="hidden"
//       animate="show"
//       viewport={{ once: true }}
//       variants={FADE_ANIMATION_VARIANTS}
//     >
//       <motion.span className={className}>{text}</motion.span>
//     </motion.div>
//   );
// }

// type FadeRectangleProps = {
//     children?: React.ReactNode; // Child content like FadeText
//     className?: string;
//     framerProps?: Variants;
//     style?: React.CSSProperties; // Custom styles for the rectangle
//   };
  
//   export function FadeRectangle({
//     children,
//     className,
//     framerProps = {
//       hidden: { opacity: 0 },
//       show: { opacity: 1, transition: { type: "spring" } },
//     },
//     style = {},
//   }: FadeRectangleProps) {
//     return (
//       <motion.div
//         initial="hidden"
//         animate="show"
//         variants={framerProps}
//         className={className}
//         style={{
//           display: "inline-block",
//           backgroundColor: "rgba(0, 0, 0, 0.7)", // Default background
//           borderRadius: "8px",
//           padding: "10px", // Add padding for text
//           ...style, // Merge custom styles
//         }}
//       >
//         {children} {/* Render text inside */}
//       </motion.div>
//     );
//   }


  

// // import { motion, Variants } from "framer-motion";
// // import React, { useMemo } from "react";
// // import { BubbleText } from "./bubbleText";

// // type FadeTextProps = {
// //   className?: string;
// //   direction?: "up" | "down" | "left" | "right";
// //   framerProps?: Variants;
// //   text: string;
// //   bubbleProps?: {
// //     fontSize?: number;
// //     borderColor?: string;
// //     backgroundColor?: string;
// //     textColor?: string;
// //   };
// // };

// // export function FadeText({
// //   direction = "up",
// //   className,
// //   framerProps = {
// //     hidden: { opacity: 0 },
// //     show: { opacity: 1, transition: { type: "spring" } },
// //   },
// //   text,
// //   bubbleProps = {},
// // }: FadeTextProps) {
// //   const directionOffset = useMemo(() => {
// //     const map = { up: 10, down: -10, left: -10, right: 10 };
// //     return map[direction];
// //   }, [direction]);

// //   const axis = direction === "up" || direction === "down" ? "y" : "x";

// //   const FADE_ANIMATION_VARIANTS = useMemo(() => {
// //     const { hidden, show, ...rest } = framerProps as {
// //       [name: string]: { [name: string]: number; opacity: number };
// //     };

// //     return {
// //       ...rest,
// //       hidden: {
// //         ...(hidden ?? {}),
// //         opacity: hidden?.opacity ?? 0,
// //         [axis]: hidden?.[axis] ?? directionOffset,
// //       },
// //       show: {
// //         ...(show ?? {}),
// //         opacity: show?.opacity ?? 1,
// //         [axis]: show?.[axis] ?? 0,
// //       },
// //     };
// //   }, [directionOffset, axis, framerProps]);

// //   return (
// //     <motion.div
// //       initial="hidden"
// //       animate="show"
// //       viewport={{ once: true }}
// //       variants={FADE_ANIMATION_VARIANTS}
// //     >
// //       <BubbleText text={text} {...bubbleProps} />
// //     </motion.div>
// //   );
// // }
