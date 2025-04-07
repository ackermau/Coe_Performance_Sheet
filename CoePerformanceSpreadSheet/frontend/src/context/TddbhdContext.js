import React, { createContext, useState } from 'react';

export const TddbhdContext = createContext();

export const TddbhdProvider = ({ children }) => {
    const [TddbhdData, setTddbhdData] = useState({
        materialTypeMax: "",
        coilWidthMax: "",
        materialThicknessMax: "",
        yieldStrengthMax: "",

        materialTypeFull: "",
        coilWidthFull: "",
        materialThicknessFull: "",
        yieldStrengthFull: "",

        materialTypeMin: "",
        coilWidthMin: "",
        materialThicknessMin: "",
        yieldStrengthMin: "",

        materialTypeWidth: "",
        coilWidthWidth: "",
        materialThicknessWidth: "",
        yieldStrengthWidth: "",
    });

    return (
        <TddbhdContext.Provider value={{ TddbhdData, setTddbhdData }}>
            {children}
        </TddbhdContext.Provider>
    );
};