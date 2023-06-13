import streamlit as st
import math
import datetime
import pdfkit as pdf
# solar house assessment app
# local directory access for pdfkit
styles = ['css/ee-report.webflow.css', 'css/normalize.css', 'css/webflow.css']  
options = {"enable-local-file-access": ""}

def error_check(home_metrics: dict):
    """Checks for errors in the survey submission."""
    # check if home_built is a valid year
    if not home_metrics["home_built"].isdigit() or not len(home_metrics["home_built"]) == 4:
        st.write("Please enter a valid year for when the home was built.")
        return True
    # check if hvac_upgrade is a valid year
    if not home_metrics["hvac_upgrade"].isdigit() or not len(home_metrics["hvac_upgrade"]) == 4:
        st.write("Please enter a valid year for when the last HVAC upgrade was made.")
        return True
    # check if insulation is a valid number
    if not isinstance(home_metrics["insulation"], int):
        st.write("Please enter a valid number for the thickness of the insulation.")
        return True
    # check if energy_consumption is a valid number
    if not isinstance(home_metrics["energy_consumption"], int):
        st.write("Please enter a valid number for the average energy consumption of the home.")
        return True
    return False

def inverse_log_clamp(value, scale):
    """Calculates the inverse log of a value and clamps it to an integer between 0 and 9."""
    inverse_log = math.exp(-value/scale)
    return min(max(int(inverse_log * 10), 0), 9)

@st.cache
def load_css(file_name = "path/to/file.css"):
    with open(file_name) as f:
        css = f'<style>{f.read()}</style>'
    return css


def load_html(file_name = "path/to/file.html"):
    with open(file_name) as f:
        html = f.read()
    return html

def evaluate(home_metrics: dict):
    # home built
    home_built = 2023 - int(home_metrics["home_built"])
    home_built = inverse_log_clamp(home_built,12)
    st.write("Home Built Score: ", home_built)
    # windows
    if home_metrics["windows"] == "Single-pane":
        windows = 1
    else:
        windows = 8
    st.write("Windows Score: ", windows)
    # hvac upgrade
    hvac_upgrade = 2023 - int(home_metrics["hvac_upgrade"])
    hvac_upgrade = inverse_log_clamp(hvac_upgrade,12)
    st.write("HVAC Upgrade Score: ", hvac_upgrade)
    # insulation
    insulation = inverse_log_clamp(home_metrics["insulation"], 12)
    st.write("Insulation Score: ", insulation)
    # thermostat
    if home_metrics["thermostat"] == "Manual":
        thermostat = 1
    elif home_metrics["thermostat"] == "Programmable":
        thermostat = 5
    else:
        thermostat = 10
    st.write("Thermostat Score: ", thermostat)
    # led: higher is better
    led = inverse_log_clamp(100 - home_metrics["led"], 100)
    st.write("LED Score: ", led)
    # renewable
    if home_metrics["renewable"] == "Yes":
        renewable = 9
    else:
        renewable = 2
    st.write("Renewable Score: ", renewable)
    # energy consumption higher is worse
    energy_consumption = inverse_log_clamp(home_metrics["energy_consumption"], 2000)
    st.write("Energy Consumption Score: ", energy_consumption)
    # shading devices
    if home_metrics["shading_devices"] == "Yes":
        shading_devices = 10
    else:
        shading_devices = 1
    st.write("Shading Devices Score: ", shading_devices)
    
    overall = math.floor((home_built + windows + hvac_upgrade + insulation + thermostat + led + renewable + energy_consumption + shading_devices) / 9)
    st.write("Overall Score: ", overall)
    

if __name__ == "__main__":
    
    
    st.title("Dynamic SLR Energy Efficiency Report ☀️")
    st.markdown("---")
    consultant_name = st.text_input("Consultant's Name")
    last_name = st.text_input("Homeowner's Last Name")
    address = st.text_input("Home Address")
    
    with st.form("Assessment"):
        
        # What year was the home built?
        # Single-pane windows or double-pane?
        # When was the last HVAC upgrade made?
        # How thick is the insulation? (thickness of insulation in inches)
        # Is your thermostat or a smart thermostat or a programmable thermostat?
        # What percentage of the light bulbs in the house are LED?
        # Any renewable energy systems installed?
        # Average energy consumption of home in terms of electricity? (kwH/month)
        # Are there any shading devices, such as awnings or window films, installed to reduce solar heat gain?

        
        # Question 1
        home_built = st.text_input("When was your home built? (YYYY)")
        # Question 2
        windows = st.selectbox("What type of windows do you have?", ("Single-pane", "Double-pane"))
        # Question 3
        hvac_upgrade = st.text_input("When was the last HVAC upgrade made? (YYYY)")
        # Question 4
        insulation = st.number_input("How thick is the insulation? (thickness of insulation in inches)", min_value=0, max_value=100, step=1)
        # Question 5
        thermostat = st.selectbox("Which type of thermostat do you have?", ("Manual", "Programmable", "Smart"))
        # Question 6
        led = st.number_input("What percentage of the light bulbs in the house are LED?", min_value=0, max_value=100, step=1)
        # Question 7
        renewable = st.selectbox("Any renewable energy systems installed?", ("Yes", "No"))
        # Question 8
        energy_consumption = st.number_input("Average energy consumption of home in terms of electricity? (kwH/month)", min_value=0, max_value=10000, step=1)
        # Question 9
        shading_devices = st.selectbox("Are there any shading devices, such as awnings or window films, installed to reduce solar heat gain?", ("Yes", "No"))
        
        submit = st.form_submit_button("Submit")
        
        if submit:
            
            home_metrics = {
                "home_built": home_built,
                "windows": windows,
                "hvac_upgrade": hvac_upgrade,
                "insulation": insulation,
                "thermostat": thermostat,
                "led": led,
                "renewable": renewable,
                "energy_consumption": energy_consumption,
                "shading_devices": shading_devices
            }
            
            error_check(home_metrics)
            
            if not error_check(home_metrics):
                
                st.write("Report for "
                            f" The {last_name} Household"" at")
                st.write(f"{address}")
                st.write("by "f"{consultant_name}")
                evaluate(home_metrics)
                date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                html = load_html("index.html")
                html = html.replace("{{consultant_name}}", consultant_name)\
                        .replace("{{last_name}}", last_name)\
                        .replace("{{date}}", date)
                 
                pdf.from_string(html, f"{last_name}_report.pdf", css=styles, options=options)
                
                st.download_button("Download Report", data=f"{last_name}_report.pdf", file_name=f"{last_name}_report.pdf")  


        
    

