import React, { createContext, useState } from 'react';

export const MaterialSpecsContext = createContext();

export const MaterialSpecsProvider = ({ children }) => {
    const [materialSpecs, setMaterialSpecs] = useState({
        // Customer Information
        customer: "",
        date: "",
        reference: "",

        // Material Specifications
        coilWidthMax: "",
        coilWeightMax: "",
        materialThicknessMax: "",
        materialTypeMax: "",
        yieldStrengthMax: "",
        materialTensileMax: "",
        requiredMaxFPMMax: "",
        minBendRadiusMax: "",
        minLoopLengthMax: "",
        coilODMax: "",
        coilIDMax: "",
        coilODCalculatedMax: "",

        coilWidthFull: "",
        coilWeightFull: "",
        materialThicknessFull: "",
        materialTypeFull: "",
        yieldStrengthFull: "",
        materialTensileFull: "",
        requiredMaxFPMFull: "",
        minBendRadiusFull: "",
        minLoopLengthFull: "",
        coilODFull: "",
        coilIDFull: "",
        coilODCalculatedFull: "",

        coilWidthMin: "",
        coilWeightMin: "",
        materialThicknessMin: "",
        materialTypeMin: "",
        yieldStrengthMin: "",
        materialTensileMin: "",
        requiredMaxFPMMin: "",
        minBendRadiusMin: "",
        minLoopLengthMin: "",
        coilODMin: "",
        coilIDMin: "",
        coilODCalculatedMin: "",

        coilWidthWidth: "",
        coilWeightWidth: "",
        materialThicknessWidth: "",
        materialTypeWidth: "",
        yieldStrengthWidth: "",
        materialTensileWidth: "",
        requiredMaxFPMWidth: "",
        minBendRadiusWidth: "",
        minLoopLengthWidth: "",
        coilODWidth: "",
        coilIDWidth: "",
        coilODCalculatedWidth: "",

        // Feed System
        feedDirection: "",
        controlsLevel: "",
        typeOfLine: "",
        feedControls: "",
        passline: "",

        // Roll Selection
        selectRoll: "",

        // Reel Information
        reelBackplate: "",
        reelStyle: "",

        // Non-Marking
        lightGaugeNonMarking: "",
        nonMarking: ""
    });

    return (
        <MaterialSpecsContext.Provider value={{ materialSpecs, setMaterialSpecs }}>
            {children}
        </MaterialSpecsContext.Provider>
    );
};
