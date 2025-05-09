import React from "react";
import { Routes, Route, Link } from "react-router-dom";
import RFQForm from "./components/RFQForm";
import MaterialSpecsForm from "./components/MaterialSpecsForm";
import EquipmentSummary from "./components/EquipmentSummary";
import TddbhdPage from "./components/TddbhdPage";
import ReelDrive from "./components/ReelDrive";
import StrUtility from "./components/StrUtility";

const navStyle = {
    backgroundColor: "#13294b",
    padding: "1rem",
    display: "flex",
    justifyContent: "space-between",
    flexWrap: "wrap",
};

const linkStyle = {
    color: "#e7a614",
    textDecoration: "none",
    fontWeight: "bold",
    margin: "0 0.5rem",
    padding: "0.5rem 1rem",
    borderRadius: "5px",
    transition: "background-color 0.3s",
};

function App() {
    return (
        <div>
            <nav style={navStyle}>
                {[
                    { path: "/", label: "Home" },
                    { path: "/rfq", label: "Create RFQ" },
                    { path: "/specs", label: "Machine Specs" },
                    { path: "/summary", label: "Equipment Summary" },
                    { path: "/tddbhd", label: "TDDBHD" },
                    { path: "/reeldrive", label: "Reel Drive" },
                    { path: "/strutility", label: "STR Utility" }
                ].map(({ path, label }) => (
                    <Link
                        key={path}
                        to={path}
                        style={linkStyle}
                        onMouseEnter={e => e.target.style.backgroundColor = "#34495e"}
                        onMouseLeave={e => e.target.style.backgroundColor = "transparent"}
                    >
                        {label}
                    </Link>
                ))}
            </nav>

            <Routes>
                <Route path="/" element={<h1>Welcome to the Performance Web Sheet</h1>} />
                <Route path="/rfq" element={<RFQForm />} />
                <Route path="/specs" element={<MaterialSpecsForm rfqId={1} />} />
                <Route path="/summary" element={<EquipmentSummary rfqId={1} />} />
                <Route path="/tddbhd" element={<TddbhdPage rfqId={1} />} />
                <Route path="/reeldrive" element={<ReelDrive rfqID={1} />} />
                <Route path="/strutility" element={<StrUtility rfqId={1} />} />
            </Routes>
        </div>
    );
}

export default App;
