import React, { createContext, useState } from 'react';

export const TddbhdContext = createContext();

export const TddbhdProvider = ({ children }) => {
    const [TddbhdData, setTddbhdData] = useState({
        materialTypeMax: "",
        materialWidthMax: "",
        materialThicknessMax: "",
        yieldStrengthMax: "",

        materialTypeFull: "",
        materialWidthFull: "",
        materialThicknessFull: "",
        yieldStrengthFull: "",

        materialTypeMin: "",
        materialWidthMin: "",
        materialThicknessMin: "",
        yieldStrengthMin: "",

        materialTypeWidth: "",
        materialWidthWidth: "",
        materialThicknessWidth: "",
        yieldStrengthWidth: "",
    });

    return (
        <TddbhdContext.Provider value={{ TddbhdData, setTddbhdData }}>
            {children}
        </TddbhdContext.Provider>
    );
};