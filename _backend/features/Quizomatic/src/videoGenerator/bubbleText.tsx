import React from 'react';

type BubbleTextProps = {
  text: string;
  fontSize?: number;
  borderColor?: string;
  backgroundColor?: string;
  textColor?: string;
  style?: React.CSSProperties; // Add style prop to accept custom styles
  isOptions: Boolean;
  optionIDX: string;
};

export const BubbleText: React.FC<BubbleTextProps> = ({
  text,
  fontSize = 70,
  borderColor = '#000',
  backgroundColor = '#fff',
  textColor = '#000',
  style, // Use the style prop
  isOptions = false,
  optionIDX =""
}) => {
  const styles: React.CSSProperties = {
    display: 'inline-block',
    padding: `${fontSize * 0.4}px ${30}px`,
    fontSize: `${fontSize}px`,
    color: textColor,
    backgroundColor: backgroundColor,
    // border: `2px solid ${borderColor}`,
    borderRadius: `${fontSize * 0.4}px`,
    textAlign: 'center',
    fontWeight: 'bold',
    marginBottom: "0px",
    width: "-webkit-fill-available",
    ...style, // Apply the custom style passed in as a prop
  };
  style?.opacity

  if (isOptions) {
    console.log("Its Options: ", optionIDX);
    return  <div style={{display:"flex", justifyContent: "start", alignItems:"center", marginBottom: "20px", opacity: style?.opacity, fontSize: fontSize}}>
                <div style={{backgroundColor:"#7a19ee", height: "100%", width: "105px", borderRadius: "20px 0px 0px 20px", display:"flex", justifyContent: "center", alignItems:"center", minHeight: "120px"}}>
                    <p style={{height: "100%", display: "flex", justifyContent: "center", alignItems: "center"}}>
                        {optionIDX=="0"? "A": optionIDX=="1"? "B" : optionIDX=="2"? "C" : optionIDX=="3"? "D" : ""  }
                    </p>
                </div>
                <div style={styles}>{text}</div>
            </div>
  }
  else{
    console.log("Not options: ", text);
    return <div style={styles}>{text}</div>;
  }
};
