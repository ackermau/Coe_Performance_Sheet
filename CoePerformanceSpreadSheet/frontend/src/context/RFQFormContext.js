// frontend/src/context/RFQFormContext.js
import React, { createContext, useState } from 'react';

export const RFQFormContext = createContext();

export const RFQFormProvider = ({ children }) => {
    const [rfqForm, setRFQForm] = useState({
        rfq_date: "",
        company_name: "",
        state_province: "",
        street_address: "",
        zip_code: "",
        city: "",
        country: "",
        contact_name: "",
        contact_position: "",
        contact_phone: "",
        contact_email: "",
        dealer_name: "",
        dealer_salesman: "",

        number_days_running: "",
        number_of_shifts: "",
        line_application: "",
        line_type: "",
        pull_through: false,
        max_coil_width: "",
        min_coil_width: "",
        coil_inner_diameter: "",
        max_coil_weight: "",
        max_coil_outside_diameter: "",
        max_coil_handling_capacity: "",
        slit_edge: false,
        mill_edge: false,
        coil_car_required: false,
        running_off_backplate: false,
        require_rewinding: false,

        max_yield_thickness: "",
        max_yield_material_type: "",
        max_yield_strength: "",
        max_yield_at_width: "",
        max_yield_tensile_strength: "",

        max_material_thickness: "",
        max_material_material_type: "",
        max_material_strength: "",
        max_material_at_width: "",
        max_material_tensile_strength: "",

        min_material_thickness: "",
        min_material_material_type: "",
        min_material_strength: "",
        min_material_at_width: "",
        min_material_tensile_strength: "",

        max_material_run_thickness: "",
        max_material_run_material_type: "",
        max_material_run_strength: "",
        max_material_run_at_width: "",
        max_material_run_tensile_strength: "",
        cosmetic: false,
        current_brand_feed_equipment: "",

        gap_frame_press: false,
        obi: false,
        shear_die_application: false,
        hydraulic_press: false,
        servo_press: false,
        straight_side_press: false,
        other: false,
        tonnage_of_press: "",
        press_bed_area_width: "",
        press_bed_area_length: "",
        press_stroke_length: "",
        window_opening_size: "",
        press_max_spm: "",
        transfer_dies: false,
        progressive_dies: false,
        blanking_dies: false,

        average_feed_length: "",
        average_spm: "",
        max_feed_length: "",
        min_feed_length: "",
        feed_window_degrees: "",
        press_cycle_time: "",
        voltage_required: "",
        alloted_length: "",
        alloted_width: "",
        feed_mounted_press: false,
        adequate_support: false,

        custom_mounting_plates: false,
        passline_height: "",
        loop_pit: false,
        coil_change_time_concern: false,
        coil_change_time_goal: "",
        feed_direction: "",
        coil_loading: "",
        guarding_safety: "",

        decision_date: "",
        ideal_delivery_date: "",
        earliest_date_excpect_delivery: "",
        latest_date_excpect_delivery: "",
        special_consideration: "",
    });

    return (
        <RFQFormContext.Provider value={{ rfqForm, setRFQForm }}>
            {children}
        </RFQFormContext.Provider>
    );
};
