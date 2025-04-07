import { useState } from "react";

export function useSharedMaterialView(labelOverrides = {}) {
    const [activeView, setActiveView] = useState("max");

    const viewConfigs = {
        max: {
            title: labelOverrides.max || "Maximum Material Specs",
            fields: [
                "materialTypeMax", "coilWidthMax", "materialThicknessMax", "yieldStrengthMax", "yieldTensileMax"
            ]
        },
        full: {
            title: labelOverrides.full || "Full Width Specs",
            fields: [
                "materialTypeFull", "coilWidthFull", "materialThicknessFull", "yieldStrengthFull", "yieldTensileFull"
            ]
        },
        min: {
            title: labelOverrides.min || "Minimum Material Specs",
            fields: [
                "materialTypeMin", "coilWidthMin", "materialThicknessMin", "yieldStrengthMin", "yieldTensileMin"
            ]
        },
        width: {
            title: labelOverrides.width || "Width-Based Specs",
            fields: [
                "materialTypeWidth", "coilWidthWidth", "materialThicknessWidth", "yieldStrengthWidth", "yieldTensileWidth"
            ]
        }
    };

    return { activeView, setActiveView, viewConfigs };
}
