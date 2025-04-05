"""
Generates two types of analysis for the call transcript(displayed via 2 tabs):-
1. Sentiment analysis:
    - Generates gauge charts to visualise the net or speaker level percentage of positive, negetive and neutral sentiments.
    - Highlights the sentiment of each interaction between the Handler and the client in the call transcript.

2. Guideline compliance:
    - Generates analytics on the guidelines followed/violated by the handler(such Greetings, PII violation, Amount of time spoken etc).
    - Generates Summary of all the guidelines followed/violated by the handler
    - Highlights the guideline followed/violated in each interaction between the Handler and the client in the call transcript.
"""

import streamlit as st
import plotly.graph_objects as go
from functionality.text2json import text_to_json
import re

st.set_page_config(page_title="Call Analysis", layout="wide", initial_sidebar_state="collapsed")

st.title("Call Analysis",)

## Prevent proceeding if no input file is provided
if "ip_file" not in st.session_state:
    st.warning("No file uploaded!")
    st.stop()

ip_file = st.session_state["ip_file"]

## Read input File
if st.session_state["file_type"]:
    content = ip_file.read()
else:
    content = ip_file.read().decode("utf-8")

## Fetch analysis for the transcript
conversation_json, attr_json,sentiment_count = text_to_json(content)


## 2 tabs for each analysis
tab1, tab2 = st.tabs(["Sentiment Analysis","Guideline Compliance"])
    
with tab1: 
    # Provides insight into the sentiment during the conversation"""
    col1, col2 = st.columns(2)

    with col1:
        #  Provides gauge visualization for sentiment analysis
        #  create tab for each of the speaker values: 'Net', 'Handler', 'Client'
        
        tabs = st.tabs(list(sentiment_count['speakers'].keys()))

        # Iterate the tabs for Handler/Client/Overall
        for i, (speaker, sentiment) in enumerate(sentiment_count['speakers'].items()):
            with tabs[i]:  # Assign each tab to a speaker
                st.subheader(f"{speaker} Sentiment Analysis")
                
                # Compute sentiment percentages
                total_sp_sentiments = sentiment['positive'] + sentiment['neutral'] + sentiment['negative']
                if total_sp_sentiments != 0:
                    sp_positive = (sentiment['positive'] / total_sp_sentiments) * 100
                    sp_neutral = (sentiment['neutral'] / total_sp_sentiments) * 100
                    sp_negative = (sentiment['negative'] / total_sp_sentiments) * 100
                else:
                    sp_positive = 0
                    sp_neutral = 0
                    sp_negative = 0

                # Create Gauge for each sentiment
                fig_sp_positive = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=sp_positive,
                    title={'text': f"{speaker} - Positive"},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "green"}}
                ))

                fig_sp_neutral = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=sp_neutral,
                    title={'text': f"{speaker} - Neutral"},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "gray"}}
                ))

                fig_sp_negative = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=sp_negative,
                    title={'text': f"{speaker} - Negative"},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "red"}}
                ))

                # Display each of the charts in repectiv columns
                sp_col1, sp_col2, sp_col3 = st.columns(3)
                with sp_col1:
                    st.plotly_chart(fig_sp_positive, use_container_width=True)
                with sp_col2:
                    st.plotly_chart(fig_sp_neutral, use_container_width=True)
                with sp_col3:
                    st.plotly_chart(fig_sp_negative, use_container_width=True)
    
    with col2:
        # Provides sentiment of each interaction between the handler and the client, and displays it in the transcript as per 
        # the color theme shown in the gauge
        st.header("Call Transcript")
        for entry in conversation_json:
            col = ":grey[" ## Default for Neutral sentiment
            
            if entry['sentiment'] == 'positive':
                col = ":green["
                
            elif entry['sentiment'] == 'negative':
                col = ":red["

            text = entry['text']
            for word in entry['prohibited_words']:
                text = text.replace(word, '----')
            
            if entry['pil_category']:
                text = re.sub(r'\d[\d-]*\d', '----', text)  # Replaces numbers with '----'

                
            if entry["speaker"] == "SPEAKER_01":
                # Handler's text
                st.markdown( f" :blue[**Handler:**] {col}**{text.strip()}**]",unsafe_allow_html=True)
            else:
                # Client's text
                st.markdown( f":orange[**Client:**] {col}**{text.strip()}**]",unsafe_allow_html=True,)


with tab2:
    # Provides insight into the Guideline compliance during the conversation"""
    col1, col2 = st.columns(2)
    ## Call Transcript with guidance complaince related interactions highlighted
    with col2:
        st.header("Call Transcript")
        for entry in conversation_json:
            col = ":grey["  ## Default non Guidance related entries

            ## Handle cases where the opening and closing statement are almost identical
            ## Remove 'Closing_Statements' from 'req_phrase_cat' and update total_closures count if start_time == 0.0. 
            if entry['start_time'] == 0.0 and "Closing_Statements" in entry['req_phrase_cat']:
                entry['req_phrase_cat'].remove("Closing_Statements")
                attr_json['total_closures'] = attr_json['total_closures'] - 1

            ## Color code text based on Guideline followed or violated
            if entry['prohibited_words']:
                col = ":red["
            elif entry['pil_category']:
                col = ":violet["
            elif entry['req_phrase_cat']:
                col = ":green["

            text = entry['text']
            for word in entry['prohibited_words']:
                text = text.replace(word, '----')
            
            if entry['pil_category']:
                text = re.sub(r'\d[\d-]*\d', '----', text)  # Replaces numbers  with '----'
            
            ## Append a Guideline related tag to the entry to highlight the nature of the compliance/violation
            if "Disclaimers" in entry['req_phrase_cat']:
                text += " [DISCLAIMER]"
            if "Greetings" in entry['req_phrase_cat']:
                text += " [GREETING]"
            if "Closing_Statements" in entry['req_phrase_cat']:
                text += " [CLOSURE]"
            if entry['prohibited_words']:  
                text += " [PROHIBITED WORDS USED]"
            if entry['pil_category']:
                text += " [PII VIOLATION]"

            if entry["speaker"] == "SPEAKER_01":
                # Handler's final text
                st.markdown( f" :blue[**Handler:**] {col}**{text.strip()}**]",unsafe_allow_html=True)
            else:
                # Client's final text
                st.markdown( f":orange[**Client:**] {col}**{text.strip()}**]",unsafe_allow_html=True,)

    with col1:
        # Provides visualizations for the Guideline compliance during the conversation"""
        tab3, tab4 = st.tabs(["Guideline Analysis","Guideline Summary"])
        with tab3:
            # Provides relevant visualizations for the Guideline followed/violated"""
            col3, col4, col5, col6, col7 = st.columns(5)
            with col3:
                st.metric(label="**:green[Total Greetings:]**", value=attr_json['total_greetings'])     
            with col4:
                st.metric(label="**:green[Total Disclaimers:]**", value=attr_json['total_disclaimers'])     
            with col5:
                st.metric(label="**:green[Total Closures:]**", value=attr_json['total_closures'])    
            with col6:
                st.metric(label="**:violet[Total PII Violation:]**", value=attr_json['total_pil'])    
            with col7:
                st.metric(label="**:red[Total Prohibited Words:]**", value=attr_json['total_prohibited_words'])   

            # Charts for Handler vs client talk time and talk speed
            st.header("Speaker Statistics")
            time_labels = ['Handler', 'Client']
            time_values = [attr_json['total_agent_time'], attr_json['total_customer_time']]
            words_labels = ['Handler', 'Client']
            words_values = [round(attr_json['total_agent_words']/attr_json['total_agent_time'], 2), round(attr_json['total_customers_words']/ attr_json['total_customer_time'], 2)]

            col8, col9 = st.columns(2)
            with col8:
                fig_time = go.Figure(data=[go.Pie(labels=time_labels, values=time_values,marker=dict(colors=['blue', 'orange']))])
                fig_time.update_layout( title="Talk Time Split",  height=400)
                st.plotly_chart(fig_time, use_container_width=True)  
            with col9: 
                fig_words = go.Figure(data=[go.Bar(y=words_labels, x=words_values,  orientation='h',marker=dict(color=['blue', 'orange']))] )
                fig_words.update_layout( title="Conversation Speed ", xaxis_title="Words per Second", yaxis_title="Speaker", height=400)
                st.plotly_chart(fig_words, use_container_width=True)
        
        with tab4:
            # Dynamically generates a summary for the guidelines followed or violated across parameters during the interaction"""
            good_signs = []
            bad_signs = []
            
            total_talk_time = attr_json['total_agent_time'] + attr_json['total_customer_time']
            if total_talk_time > 0: 
                agent_talk_percentage = (attr_json['total_agent_time'] / total_talk_time) * 100
            else:
                agent_talk_percentage = 0

            ## Ratio of time agent talked for
            if agent_talk_percentage > 70:
                bad_signs.append(f"🔴 Handler dominated the conversation duration, with a {agent_talk_percentage:.2f}% talk time.")
            else:
                good_signs.append(f"🟢 Handler was concise with time, having used {agent_talk_percentage:.2f}% of the talk time.")

            agent_conv_speed = round(attr_json['total_agent_words']/attr_json['total_agent_time'], 2)
            ## Ratio of words used by the Handler wrt to client
            if agent_conv_speed > 2.5:
                bad_signs.append(f"🔴 On an average the Handler's speed was above the threshold of 2.5 WPS( WPS observed: {agent_conv_speed})")
            else:
                good_signs.append(f"🟢  On an average the Handler's speed was below the threshold of 2.5 WPS( WPS observed: {agent_conv_speed})")

            ## Atleast 1 greeting present
            if attr_json['total_greetings'] > 0:
                good_signs.append("🟢 Greetings were included.")
            else:
                bad_signs.append("🔴 Greetings were missing.")

            ## Atleast 1 disclaimer present
            if attr_json['total_disclaimers'] > 0:
                good_signs.append("🟢 Disclaimers were present.")
            else:
                bad_signs.append("🔴 Disclaimers were missing.")

            ## Atleast 1 closure present
            if attr_json['total_closures'] > 0:
                good_signs.append("🟢 Closures were handled.")
            else:
                bad_signs.append("🔴 Closures were missing.")

            ## Personally Identifiable Information violation observed or not
            if attr_json['total_pil'] > 0:
                bad_signs.append("🟣 PII leak was detected(Handler asked for account information/pin/DOB information)")
            else:
                good_signs.append("🟢 No PII leaked.")
            
            ## Any prohibited word used or not
            if attr_json['total_prohibited_words'] > 0:
                bad_signs.append("🔴 Handler used Profanity in text")
            else:
                good_signs.append("🟢 No profanity used")

            st.header("✅ **Good Signs**")
            if good_signs:
                for sign in good_signs:
                    st.markdown(f" **{sign}**")
            else:
                st.markdown("No good signs detected.")

            st.header("❌ **Bad Signs**")
            if bad_signs:
                for sign in bad_signs:
                    st.markdown(f" **{sign}**")
            else:
                st.markdown("No bad signs detected.")

    
   