import { Sequence, staticFile, useCurrentFrame, useVideoConfig, OffthreadVideo } from "remotion";
import { useEffect, useState } from "react";
import { AbsoluteFill, Audio as RemotionAudio  } from "remotion";
import { Animated, Move } from 'remotion-animated';
import { VideoNumber } from './videoNumber';


interface videoData {
  questionText: string;
  optionstext: string;
  answerText: string;
  questionAudio: string;
  optionsAudio: string;
  answerAudio: string;
  combinedAudio: string;
  backgroundImage: string;
}

type singleVideoGeneratorProps = {
  template: string;
  videoCount: number;
  videoData: videoData[]
};

export const singleVideoGenerator: React.FC<singleVideoGeneratorProps> = ({template, videoCount, videoData}) => {
  const frame = useCurrentFrame();
  const { width, height, fps } = useVideoConfig();

  let MAX_QUES_LON_WORD = 3;
  const isLandscapeVideo = width > height? true: false;
  const questionAudio =  staticFile(videoData[0].questionAudio);
  const optionsAudio =  staticFile(videoData[0].optionsAudio);
  const answerAudio =  staticFile(videoData[0].answerAudio);
  const combinedAudio = staticFile(videoData[0].combinedAudio)
  const [correctAnswer, setCorrectAnswer] =  useState("");
  const [isQuestionPositionAbsolute, setQuestionPositionAbsolute] =  useState(true);
  const [optionsVisibilitycontroller, setoptionsVisibilitycontroller] =  useState(0.0);
  const [durations, setDurations] = useState({question: 0, options: 0, answer: 0});

  useEffect(() => {
    const fetchDurations = async () => {
      const audios = [ questionAudio, optionsAudio, answerAudio];
      const durations = await Promise.all(
        audios.map((src) => {
          const audio = new Audio(src);
          return new Promise<number>((resolve) =>
            audio.addEventListener("loadedmetadata", () => resolve(audio.duration))
          );
        })
      );
      setDurations({
        question: durations[0],
        options: durations[1],
        answer: durations[2],
      });
    };
    fetchDurations();
  }, []);

  // questionText = "The human brain weighs about?";
  // answerText = "Answer is. 1.5 kg";
  // optionstext = "1 kg Testing, 1.5 kg, 2 kg, 3 kg"

  let longWordsQuestions = 0;
  let needExtraBold = false;
  let questionWords = videoData[0].questionText.split(" ");
  let optionsSplit  = videoData[0].optionstext.split(",");

  questionWords.forEach((x) => {if (x.trim().length >= 5) longWordsQuestions += 1; })
  if (longWordsQuestions < MAX_QUES_LON_WORD && videoData[0].questionText.length <= 8) needExtraBold = true;
  if (optionsSplit.length <= 1) optionsSplit = videoData[0].optionstext[0].split(", ");

  const timeline = [
    {
      type: "question",
      text: questionWords,
      audio: questionAudio,
      duration: 5,
      startFrame: 60,
    },
    {
      type: "options",
      text: optionsSplit,
      audio: optionsAudio,
      duration: 5,
      startFrame: 60 + Math.ceil(durations.question * fps) + Math.ceil(0.5 * fps),
    },
    {
      type: "timer",
      text: [""],
      duration: 10,
      startFrame:
        60 + Math.ceil(durations.question * fps) +
        Math.ceil(durations.options * fps) +
        Math.ceil(1 * fps),
    },
    {
      type: "answer",
      text: [videoData[0].answerText],
      audio: answerAudio,
      duration: 5,
      startFrame:
        60 + Math.ceil(durations.question * fps) +
        Math.ceil(durations.options * fps) +
        Math.ceil(1 * fps) +
        Math.ceil(1 * fps) +
        Math.ceil(10 * fps),
    },
  ];
  
  return (
    <>
      {videoCount > 0 && 
      // Changed Height
        <Sequence from={65} style={{ position: "relative", height: "auto", width: "100%", justifyContent: "center", marginLeft: isLandscapeVideo? "-25%" : "0"}}> 
          <Animated animations={[Move({ initialX: (width/2)-125*4, x: (width/2)-125*4, initialY: -200, y: 20 }) ]}>
            <VideoNumber number={videoCount}/>
          </Animated> 
        </Sequence>
      }
      <Sequence from={65}>
        <AbsoluteFill>
            <RemotionAudio src={combinedAudio} volume={1} /> 
        </AbsoluteFill>
      </Sequence>

      <div
        id="parentDiv"
        style={{
          width: width,
          height: height,
          backgroundColor: "gray",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          fontSize: 20,
          backgroundImage: `url(${staticFile(videoData[0].backgroundImage)})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
        }}>
            {timeline.map((event, index) => {
              const showQuestion = frame >= event.startFrame;
              const showOptions = event.type === "options" && frame >= timeline[1].startFrame;
              const showAnswer = event.type === "answer" && frame >= event.startFrame;
              const isVisible = frame >= event.startFrame && frame < event.startFrame + Math.ceil(event.text.length * fps);
              const isTimerVisible = event.type === "timer" && frame >= event.startFrame && frame < event.startFrame + event.duration * fps;
              const showTimer = event.type === "timer" && frame >= event.startFrame && frame <= event.startFrame + event.duration * fps;
              
            if (event.type === "options" && showOptions) {
              if (isQuestionPositionAbsolute === false) setQuestionPositionAbsolute(false);
            }   

            if (event.type === "answer" && showAnswer) {
              if (correctAnswer.length <= 0) {
                if (event?.text && event.text[0]) {
                  const processedText = event.text[0]
                    .split(' ')
                    .splice(2)
                    .join(' ')
                    .trim();
                  setCorrectAnswer(processedText);
                }
              }
            }     
              return (    
                (isVisible || isTimerVisible || showQuestion || showOptions || showTimer || showAnswer) && (
                  <div
                    key={index}
                    style={{
                      marginTop: 40,
                      fontSize: isLandscapeVideo? 40 : 70,
                      color: "white",
                      fontWeight: "normal",
                      display: "flex",
                      justifyContent: "center"
                    }}
                  >
                  {event.type === "question" && showQuestion && (
                    <>
                      <div
                        style={{
                          left: isLandscapeVideo? "100%" : "1000px",
                          width: width - 100,
                          height: "auto",
                          position: "relative",
                          display: "inline-block",
                          borderRadius: "8px",
                          zIndex: 0,
                          transform: "translateX(-100%)",
                          transition: "transform 1s ease-in-out",
                          borderEndEndRadius: "10px",
                          marginBottom: "50px",
                        }}
                        
                        >
                          <Animated animations={[ Move({ initialX: width, x: 0, initialY: 0, y: 0 }) ]} >
                            <div style={{
                              position: isQuestionPositionAbsolute? "relative" : "absolute",
                              top: 20,
                              left: 0,
                              width: "auto",
                              height: "auto",
                              backgroundColor: "rgb(0 0 0 / 60%)",  
                              borderRadius: "20px",
                              boxShadow: "#1b19199c 0px 10px 10px",
                              padding: "50px",
                              textWrap: "wrap",
                            }}>
                              <h1 style={{ position: "relative", zIndex: 1 }}>
                                <Sequence from={event.startFrame + 10} style={{position:"relative", display: "inline-block"}}>
                                  {event.text.map((word, idx) => (
                                    <Animated
                                      key={`animated-word-${idx}`}
                                      animations={[
                                        Move({ initialX: width, initialY: 0, x: 0, y: 0  }), 
                                      ]}
                                      style={{
                                        width: "auto",
                                        opacity: frame >= event.startFrame + idx * 7 ? 1 : 0,
                                        display: "inline-block",
                                        marginRight: "15px",
                                        fontWeight: "normal",
                                        position: "absolute",
                                      }}>
                                      <div style={{ width: "auto", fontWeight: "bold", color: "white"}}>
                                          {word}
                                      </div>
                                    </Animated>
                                  ))}
                                </Sequence>

                              </h1>
                            </div>
                        </Animated>
                      </div>
                    </>
                  )}
                  
                  {event.type === "options" && showOptions && (
                      // <div style={{width: "100%", minWidth: "400px", display: "flex", flexDirection:isLandscapeVideo? "column": "column", alignContent:"start", justifyContent: "start"}}>
                      <div style={{
                        width: isLandscapeVideo? "70%" : "100%",
                        minWidth: "400px",
                        display: "flex",
                        flexDirection: isLandscapeVideo ? "row" : "column", // Aligns items in a row
                        alignContent: "start",
                        justifyContent: isLandscapeVideo? "center": "space-between",
                        flexWrap: "wrap",
                        columnGap: isLandscapeVideo? "15px": "0", // Adds space between the divs
                        rowGap: isLandscapeVideo? "0": "15px",
                        // WebkitJustifyContent: "start",
                        transition: "all 0.5s ease-in-out", // Transition for flex container
                        alignItems: "start"
                      }}>
                        {event.text.map((option, idx) => {
                              const isCorrectedAnswer = correctAnswer === option.trim() || correctAnswer.includes(option.trim() );
                              const reqFontSize = showAnswer? longWordsQuestions < MAX_QUES_LON_WORD? isCorrectedAnswer? needExtraBold? 100 : 68: 60 : isCorrectedAnswer? needExtraBold? 90 : 53 : 45 
                              : longWordsQuestions < MAX_QUES_LON_WORD? isCorrectedAnswer && showAnswer? needExtraBold? 100 : 68: 60 : isCorrectedAnswer && showAnswer? needExtraBold? 90 : 53 : 45;                
                              if (showOptions && optionsVisibilitycontroller<=5.0){ 
                                setoptionsVisibilitycontroller( optionsVisibilitycontroller+1.5); 
                                console.log(optionsVisibilitycontroller);
                              }
                              return (
                                <Sequence key={`option-animated-seq${idx}`} from={event.startFrame + idx * durations.options * 7} style={{ width: isLandscapeVideo? "fit-content":"-webkit-fill-available", minWidth :"350px", height: isLandscapeVideo? "fit-content":"-webkit-fill-available", position:"relative", display: "inline-block"}}>
                                  <Animated key={`option-animated-ani-${idx}`}
                                      animations={[Move({ initialX: width, initialY: 0, x: 0, y: 0  })]}
                                      style={{
                                        width: isLandscapeVideo? "500px": "-webkit-fill-available",
                                        opacity: frame >= event.startFrame + idx * 7 ? 1 : 0,
                                        display: "inline-block",
                                        marginRight: "15px",
                                        fontWeight: "normal",
                                        position: "absolute",
                                        minWidth: isLandscapeVideo? "500px": "400px",
                                        overflow: "hidden",
                                        transition: "transform 0.05s ease-in-out", // Smooth transition for the div
                                    }}> 
                                    <div key={`option-animated-ani-div1-${idx}`} style={{display:"flex", justifyContent: "start", alignItems:"center", marginBottom: isLandscapeVideo? "20px": "0", opacity: frame >= event.startFrame + idx * durations.options * 7 ? 1 : 0, fontSize: reqFontSize}}>
                                        <div key={`option-animated-ani-div1-div1-${idx}`} style={{backgroundColor:"#7a19ee", height: "100%", width: "105px", borderRadius: "20px 0px 0px 20px", display:"flex", justifyContent: "center", alignItems:"center", minHeight: "120px"}}>
                                            <p style={{height: "100%", display: "flex", justifyContent: "center", alignItems: "center", fontSize: isLandscapeVideo? "4.5vh": reqFontSize }}>
                                                {idx==0? "A": idx==1? "B" : idx==2? "C" : idx==3? "D" : ""  }
                                            </p>
                                        </div>
                                        <div key={`option-animated-ani-div1-div2-${idx}`} style={{
                                          opacity: frame >= event.startFrame + idx * durations.options * 7 ? 1 : 0,
                                          textAlign: "start",
                                          display:"flex",
                                          flexDirection:"column",
                                          borderRadius: "0px 20px 20px 0px",
                                          boxShadow: "2px 2px 5px #80808080",
                                          width: "-webkit-fill-available",
                                          height: "100%",
                                          justifyContent: "center", 
                                          alignItems: "center",
                                          backgroundColor: isCorrectedAnswer? "rgba(0, 128, 0, 0.7)" : "#cdc7c7",
                                          color: isCorrectedAnswer? "white" : "black",
                                          minHeight: "120px",
                                          fontSize: isLandscapeVideo? "4vh" : reqFontSize,
                                          fontWeight: "bold",
                                          borderColor:"#00796b",
                                          padding: "0px 10px",
                                          overflow: "hidden",
                                          transition: "transform 0.05s ease-in-out",
                                        }}>{option}</div>
                                    </div>
                                  </Animated>
                                </Sequence>
                              );
                          })}
                      </div>
                    )}
                    {event.type === "timer" && showTimer && (
                      <div style={{ width: isLandscapeVideo? "250px" : "300px", height: isLandscapeVideo? "250px" : "300px", marginTop: isLandscapeVideo? "-40px" : "-20px", display: "flex", justifyContent: "center", alignItems: "end" }}>
                      <Sequence from={event.startFrame}
                      style={{
                        position: "relative",
                        top: isLandscapeVideo? "8vh": "0"
                      }}
                      >
                        <OffthreadVideo
                          src={staticFile('timer.mp4')}
                          style={{
                            mixBlendMode: 'screen',
                            width: isLandscapeVideo? "250px" : "300px",
                            height:  isLandscapeVideo? "250px" : "300px",
                          }}
                        />
                      </Sequence>
                    </div>  
                    )}
                  </div>
                )
              );
            })}
      </div>
    </>
  );
};