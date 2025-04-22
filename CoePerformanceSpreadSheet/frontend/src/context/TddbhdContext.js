import React, { createContext, useState, useEffect } from 'react';

export const TddbhdContext = createContext();

export const TddbhdProvider = ({ children }) => {
    const defaultSubpageData = {
        page1: {}, // Max
        page2: {}, // Full
        page3: {}, // Min
        page4: {}, // Width
    };

    const [subpageData, setSubpageData] = useState(defaultSubpageData);
    const [activePage, setActivePage] = useState("page1");

    // Load from localStorage on mount
    useEffect(() => {
        const saved = localStorage.getItem("tddbhdState");
        if (saved) {
            const parsed = JSON.parse(saved);
            if (parsed.subpageData) setSubpageData(parsed.subpageData);
            if (parsed.activePage) setActivePage(parsed.activePage);
        }
    }, []);

    // Save to localStorage on update
    useEffect(() => {
        localStorage.setItem("tddbhdState", JSON.stringify({ subpageData, activePage }));
    }, [subpageData, activePage]);

    return (
        <TddbhdContext.Provider value={{
            subpageData,
            setSubpageData,
            activePage,
            setActivePage
        }}>
            {children}
        </TddbhdContext.Provider>
    );
};
