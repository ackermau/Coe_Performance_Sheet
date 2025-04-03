import { useState } from "react";

export function useSharedMaterialView(labelOverrides = {}) {
    const [activeView, setActiveView] = useState("max");

    const viewConfigs = {
        max: {
            title: labelOverrides.max || "Maximum Material Specs",
            fields: [
                "materialTypeMax", "materialWidthMax", "materialThicknessMax", "yieldStrengthMax", "yieldTensileMax"
            ]
        },
        full: {
            title: labelOverrides.full || "Full Width Specs",
            fields: [
                "materialTypeFull", "materialWidthFull", "materialThicknessFull", "yieldStrengthFull", "yieldTensileFull"
            ]
        },
        min: {
            title: labelOverrides.min || "Minimum Material Specs",
            fields: [
                "materialTypeMin", "materialWidthMin", "materialThicknessMin", "yieldStrengthMin", "yieldTensileMin"
            ]
        },
        width: {
            title: labelOverrides.width || "Width-Based Specs",
            fields: [
                "materialTypeWidth", "materialWidthWidth", "materialThicknessWidth", "yieldStrengthWidth", "yieldTensileWidth"
            ]
        }
    };

    return { activeView, setActiveView, viewConfigs };
}
