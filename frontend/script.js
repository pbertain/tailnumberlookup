// Frontend JavaScript for Tail Number Lookup

// Field display configuration
const fieldsToShow = {
    "n_number": "N-Number",
    "serial_number": "Serial Number",
    "aircraft_manufacturer_name": "Aircraft Manufacturer",
    "aircraft_model_name": "Aircraft Model",
    "year_mfr": "Year Manufactured",
    "number_of_engines": "Number of Engines",
    "number_of_seats": "Number of Seats",
    "engine_manufacturer_name": "Engine Manufacturer",
    "engine_model_name": "Engine Model",
    "horsepower": "Horsepower",
    "pounds_of_thrust": "Thrust (lbs)",
    "registrant_name": "Registrant Name",
    "street1": "Street Address",
    "street2": "Street Address 2",
    "city": "City",
    "state": "State",
    "zip_code": "Zip Code",
    "country_mail_code": "Country Code",
    "last_activity_date": "Last Activity Date",
    "cert_issue_date": "Certificate Issue Date",
    "cert_requested": "Certification Requested",
    "type_aircraft": "Aircraft Type",
    "type_engine": "Engine Type",
    "status_code": "Status Code",
    "mode_s_code": "Mode S Code",
    "fractional_ownership": "Fractional Ownership",
    "airworthiness_date": "Airworthiness Date",
    "expiration_date": "Expiration Date",
    "unique_id": "Unique ID",
    "kit_mfr": "Kit Manufacturer",
    "kit_model_code": "Kit Model Code",
    "mode_s_code_hex": "Mode S Code (Hex)"
};

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
    // Check for tail number in URL
    const urlParams = new URLSearchParams(window.location.search);
    const tailNumber = urlParams.get("nNumber") || urlParams.get("tailNumber");
    
        if (tailNumber) {
        // Remove N prefix for display
        const displayValue = tailNumber.replace(/^N/i, "").toUpperCase();
        document.getElementById("tailNumber").value = displayValue;
        searchAircraft(null, displayValue);
    }
    
    // Set up form handler
    const form = document.getElementById("searchForm");
    const input = document.getElementById("tailNumber");
    
    // Auto-uppercase and remove 'N' prefix as user types (for display only)
    input.addEventListener("input", (e) => {
        let value = e.target.value.toUpperCase().replace(/^N/, '').replace(/[^0-9A-Z]/g, '');
        // Limit to 5 characters
        if (value.length > 5) {
            value = value.slice(0, 5);
        }
        e.target.value = value;
    });
    
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const value = input.value.trim().toUpperCase().replace(/^N/, '');
        if (value) {
            // API handles case-insensitivity, but we'll send uppercase
            searchAircraft(e, value);  // Send without N prefix, API will add it
        }
    });
    
    // Store search history in localStorage
    loadSearchHistory();
});

// Search for aircraft
async function searchAircraft(event, tailNumber = null) {
    if (event) event.preventDefault();
    
    // Normalize: remove N prefix if present, uppercase, API will handle case-insensitivity
    let searchValue = tailNumber || document.getElementById("tailNumber").value.trim().toUpperCase();
    if (!searchValue) return;
    
    // Remove N prefix if user included it
    searchValue = searchValue.replace(/^N/, '');
    
    const resultDiv = document.getElementById("result");
    const loadingDiv = document.getElementById("loading");
    
    // Clear previous results
    resultDiv.innerHTML = "";
    resultDiv.classList.add("hidden");
    
    // Show loading
    loadingDiv.classList.remove("hidden");
    
    try {
        const response = await fetch(`/api/v1/aircraft/${encodeURIComponent(searchValue)}`);
        
        if (response.ok) {
            const data = await response.json();
            displayResults(data);
            
            // Save to search history
            saveToHistory(searchValue);
            
            // Update URL without reload
            const newUrl = new URL(window.location);
            newUrl.searchParams.set("tailNumber", searchValue);
            window.history.pushState({}, "", newUrl);
        } else {
            if (response.status === 404) {
                displayError(`Aircraft with tail number ${searchValue} not found.`);
            } else {
                displayError(`Error: ${response.status} ${response.statusText}`);
            }
        }
    } catch (error) {
        console.error("Error fetching aircraft data:", error);
        displayError("Network error. Please check your connection and try again.");
    } finally {
        loadingDiv.classList.add("hidden");
    }
}

// Display results
function displayResults(data) {
    const resultDiv = document.getElementById("result");
    resultDiv.classList.remove("hidden");
    
    let table = `<div class="result-success">`;
    table += `<h3 style="color: var(--airpuff-primary); margin-bottom: 1rem;">Aircraft Information</h3>`;
    table += `<table class="styled-table"><tbody>`;
    
    // Display fields in order
    for (const [key, label] of Object.entries(fieldsToShow)) {
        if (data[key] !== undefined && data[key] !== null && data[key] !== "") {
            let value = data[key];
            
            // Format dates
            if (key.includes("date") && value) {
                try {
                    const date = new Date(value);
                    if (!isNaN(date.getTime())) {
                        value = date.toLocaleDateString("en-US", {
                            year: "numeric",
                            month: "long",
                            day: "numeric"
                        });
                    }
                } catch (e) {
                    // Keep original value if date parsing fails
                }
            }
            
            table += `<tr><th>${label}</th><td>${value}</td></tr>`;
        }
    }
    
    table += `</tbody></table></div>`;
    resultDiv.innerHTML = table;
}

// Display error
function displayError(message) {
    const resultDiv = document.getElementById("result");
    resultDiv.classList.remove("hidden");
    resultDiv.innerHTML = `<div class="result-error"><p>${message}</p></div>`;
}

// Search history (localStorage)
function saveToHistory(tailNumber) {
    try {
        const history = JSON.parse(localStorage.getItem("searchHistory") || "[]");
        // Add to beginning, remove duplicates, limit to 10
        const updated = [tailNumber, ...history.filter(h => h !== tailNumber)].slice(0, 10);
        localStorage.setItem("searchHistory", JSON.stringify(updated));
    } catch (e) {
        // Ignore localStorage errors
    }
}

function loadSearchHistory() {
    // Could display history dropdown in future enhancement
    try {
        const history = JSON.parse(localStorage.getItem("searchHistory") || "[]");
        if (history.length > 0) {
            // History available for future features
        }
    } catch (e) {
        // Ignore
    }
}

