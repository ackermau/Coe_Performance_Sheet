import React, { createContext, useState } from 'react';

export const ReelDriveContext = createContext();

export const ReelDriveProvider = ({ children }) => {
    const [reelDriveData, setReelDriveData] = useState({
        // User Inputs
        model: "CPR-200",
        material_type: "Cold Rolled Steel",
        coil_weight: 15000,
        coil_id: 20,
        coil_od: 60,
        reel_width: 72,
        backplate_diameter: 72,
        motor_hp: 30,
        type_of_line: "Compact",
        required_max_fpm: 200,

        // Backend Results (populated after API call)
        reel: "",
        mandrel: "",
        backplate: "",
        coil: "",
        reducer: "",
        chain: "",
        total: "",
        motor: "",
        friction: "",
        torque: "",
        hp_req: "",
        regen: "",
        use_pulloff: "",
        speed: null,
        accel_rate: 1,
        accel_time: null,

        torque_empty: ""
    });

    return (
        <ReelDriveContext.Provider value={{ reelDriveData, setReelDriveData }}>
            {children}
        </ReelDriveContext.Provider>
    );
};
