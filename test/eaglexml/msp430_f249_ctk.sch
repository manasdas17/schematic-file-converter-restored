<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE eagle SYSTEM "eagle.dtd">
<eagle version="6.1">
<drawing>
<settings>
<setting alwaysvectorfont="no"/>
<setting verticaltext="up"/>
</settings>
<grid distance="0.1" unitdist="inch" unit="inch" style="lines" multiple="1" display="no" altdistance="0.01" altunitdist="inch" altunit="inch"/>
<layers>
<layer number="1" name="Top" color="4" fill="1" visible="no" active="no"/>
<layer number="16" name="Bottom" color="1" fill="1" visible="no" active="no"/>
<layer number="17" name="Pads" color="2" fill="1" visible="no" active="no"/>
<layer number="18" name="Vias" color="2" fill="1" visible="no" active="no"/>
<layer number="19" name="Unrouted" color="6" fill="1" visible="no" active="no"/>
<layer number="20" name="Dimension" color="15" fill="1" visible="no" active="no"/>
<layer number="21" name="tPlace" color="7" fill="1" visible="no" active="no"/>
<layer number="22" name="bPlace" color="7" fill="1" visible="no" active="no"/>
<layer number="23" name="tOrigins" color="15" fill="1" visible="no" active="no"/>
<layer number="24" name="bOrigins" color="15" fill="1" visible="no" active="no"/>
<layer number="25" name="tNames" color="7" fill="1" visible="no" active="no"/>
<layer number="26" name="bNames" color="7" fill="1" visible="no" active="no"/>
<layer number="27" name="tValues" color="7" fill="1" visible="no" active="no"/>
<layer number="28" name="bValues" color="7" fill="1" visible="no" active="no"/>
<layer number="29" name="tStop" color="7" fill="3" visible="no" active="no"/>
<layer number="30" name="bStop" color="7" fill="6" visible="no" active="no"/>
<layer number="31" name="tCream" color="7" fill="4" visible="no" active="no"/>
<layer number="32" name="bCream" color="7" fill="5" visible="no" active="no"/>
<layer number="33" name="tFinish" color="6" fill="3" visible="no" active="no"/>
<layer number="34" name="bFinish" color="6" fill="6" visible="no" active="no"/>
<layer number="35" name="tGlue" color="7" fill="4" visible="no" active="no"/>
<layer number="36" name="bGlue" color="7" fill="5" visible="no" active="no"/>
<layer number="37" name="tTest" color="7" fill="1" visible="no" active="no"/>
<layer number="38" name="bTest" color="7" fill="1" visible="no" active="no"/>
<layer number="39" name="tKeepout" color="4" fill="11" visible="no" active="no"/>
<layer number="40" name="bKeepout" color="1" fill="11" visible="no" active="no"/>
<layer number="41" name="tRestrict" color="4" fill="10" visible="no" active="no"/>
<layer number="42" name="bRestrict" color="1" fill="10" visible="no" active="no"/>
<layer number="43" name="vRestrict" color="2" fill="10" visible="no" active="no"/>
<layer number="44" name="Drills" color="7" fill="1" visible="no" active="no"/>
<layer number="45" name="Holes" color="7" fill="1" visible="no" active="no"/>
<layer number="46" name="Milling" color="3" fill="1" visible="no" active="no"/>
<layer number="47" name="Measures" color="7" fill="1" visible="no" active="no"/>
<layer number="48" name="Document" color="7" fill="1" visible="no" active="no"/>
<layer number="49" name="Reference" color="7" fill="1" visible="no" active="no"/>
<layer number="50" name="dxf" color="7" fill="1" visible="no" active="no"/>
<layer number="51" name="tDocu" color="7" fill="1" visible="no" active="no"/>
<layer number="52" name="bDocu" color="7" fill="1" visible="no" active="no"/>
<layer number="53" name="tGND_GNDA" color="7" fill="9" visible="no" active="no"/>
<layer number="54" name="bGND_GNDA" color="1" fill="9" visible="no" active="no"/>
<layer number="56" name="wert" color="7" fill="1" visible="no" active="no"/>
<layer number="91" name="Nets" color="2" fill="1" visible="yes" active="yes"/>
<layer number="92" name="Busses" color="1" fill="1" visible="yes" active="yes"/>
<layer number="93" name="Pins" color="2" fill="1" visible="no" active="yes"/>
<layer number="94" name="Symbols" color="4" fill="1" visible="yes" active="yes"/>
<layer number="95" name="Names" color="7" fill="1" visible="yes" active="yes"/>
<layer number="96" name="Values" color="7" fill="1" visible="yes" active="yes"/>
<layer number="97" name="Info" color="7" fill="1" visible="yes" active="yes"/>
<layer number="98" name="Guide" color="6" fill="1" visible="yes" active="yes"/>
<layer number="100" name="Muster" color="7" fill="1" visible="yes" active="yes"/>
<layer number="101" name="Flex-Kleb" color="1" fill="7" visible="yes" active="yes"/>
<layer number="102" name="fp2" color="7" fill="1" visible="yes" active="yes"/>
<layer number="103" name="fp3" color="7" fill="1" visible="yes" active="yes"/>
<layer number="104" name="fp4" color="7" fill="1" visible="yes" active="yes"/>
<layer number="105" name="Beschreib" color="9" fill="1" visible="yes" active="yes"/>
<layer number="106" name="BGA-Top" color="4" fill="1" visible="yes" active="yes"/>
<layer number="107" name="BD-Top" color="5" fill="1" visible="yes" active="yes"/>
<layer number="108" name="fp8" color="7" fill="1" visible="yes" active="yes"/>
<layer number="109" name="fp9" color="7" fill="1" visible="yes" active="yes"/>
<layer number="110" name="fp0" color="7" fill="1" visible="yes" active="yes"/>
<layer number="116" name="Patch_BOT" color="9" fill="4" visible="yes" active="yes"/>
<layer number="121" name="tTestdril" color="7" fill="1" visible="yes" active="yes"/>
<layer number="122" name="bTestdril" color="7" fill="1" visible="yes" active="yes"/>
<layer number="123" name="tTestmark" color="7" fill="1" visible="yes" active="yes"/>
<layer number="124" name="bTestmark" color="7" fill="1" visible="yes" active="yes"/>
<layer number="125" name="_tNames" color="7" fill="1" visible="no" active="yes"/>
<layer number="131" name="tAdjust" color="7" fill="1" visible="yes" active="yes"/>
<layer number="132" name="bAdjust" color="7" fill="1" visible="yes" active="yes"/>
<layer number="144" name="Drill_legend" color="7" fill="1" visible="no" active="yes"/>
<layer number="151" name="HeatSink" color="7" fill="1" visible="no" active="yes"/>
<layer number="200" name="200bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="201" name="201bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="202" name="202bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="203" name="203bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="204" name="204bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="205" name="205bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="206" name="206bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="207" name="207bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="208" name="208bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="209" name="209bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="210" name="210bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="211" name="211bmp" color="7" fill="1" visible="no" active="yes"/>
<layer number="212" name="212bmp" color="7" fill="1" visible="no" active="yes"/>
<layer number="213" name="213bmp" color="7" fill="1" visible="no" active="yes"/>
<layer number="214" name="214bmp" color="7" fill="1" visible="no" active="yes"/>
<layer number="215" name="215bmp" color="7" fill="1" visible="no" active="yes"/>
<layer number="216" name="216bmp" color="7" fill="1" visible="no" active="yes"/>
<layer number="217" name="217bmp" color="18" fill="1" visible="no" active="no"/>
<layer number="218" name="218bmp" color="19" fill="1" visible="no" active="no"/>
<layer number="219" name="219bmp" color="20" fill="1" visible="no" active="no"/>
<layer number="220" name="220bmp" color="21" fill="1" visible="no" active="no"/>
<layer number="221" name="221bmp" color="22" fill="1" visible="no" active="no"/>
<layer number="222" name="222bmp" color="23" fill="1" visible="no" active="no"/>
<layer number="223" name="223bmp" color="24" fill="1" visible="no" active="no"/>
<layer number="224" name="224bmp" color="25" fill="1" visible="no" active="no"/>
<layer number="250" name="Descript" color="3" fill="1" visible="no" active="no"/>
<layer number="251" name="SMDround" color="12" fill="11" visible="no" active="no"/>
<layer number="254" name="OrgLBR" color="7" fill="1" visible="yes" active="yes"/>
</layers>
<schematic xreflabel="%F%N/%S.%C%R" xrefpart="/%S.%C%R">
<libraries>
<library name="TI_MSP430_v16">
<packages>
<package name="PM/PAG64">
<description>*** TI: PM *** JEDEC: S-PQFP-G64 *** 64 PINS ***</description>
<wire x1="-5" y1="-5" x2="5" y2="-5" width="0.127" layer="21"/>
<wire x1="5" y1="-5" x2="5" y2="5" width="0.127" layer="21"/>
<wire x1="5" y1="5" x2="-5" y2="5" width="0.127" layer="21"/>
<wire x1="-5" y1="5" x2="-5" y2="-5" width="0.127" layer="21"/>
<circle x="-4.365" y="4.398" radius="0.2839" width="0.127" layer="21"/>
<smd name="17" x="-3.75" y="-5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="18" x="-3.25" y="-5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="19" x="-2.75" y="-5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="20" x="-2.25" y="-5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="21" x="-1.75" y="-5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="22" x="-1.25" y="-5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="23" x="-0.75" y="-5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="24" x="-0.25" y="-5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="25" x="0.25" y="-5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="26" x="0.75" y="-5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="27" x="1.25" y="-5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="28" x="1.75" y="-5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="29" x="2.25" y="-5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="30" x="2.75" y="-5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="31" x="3.25" y="-5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="32" x="3.75" y="-5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="64" x="-3.75" y="5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="63" x="-3.25" y="5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="62" x="-2.75" y="5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="61" x="-2.25" y="5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="60" x="-1.75" y="5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="59" x="-1.25" y="5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="58" x="-0.75" y="5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="57" x="-0.25" y="5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="56" x="0.25" y="5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="55" x="0.75" y="5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="54" x="1.25" y="5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="53" x="1.75" y="5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="52" x="2.25" y="5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="51" x="2.75" y="5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="50" x="3.25" y="5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="49" x="3.75" y="5.8" dx="0.3" dy="1.4" layer="1"/>
<smd name="1" x="-5.8" y="3.75" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="2" x="-5.8" y="3.25" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="3" x="-5.8" y="2.75" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="4" x="-5.8" y="2.25" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="5" x="-5.8" y="1.75" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="6" x="-5.8" y="1.25" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="7" x="-5.8" y="0.75" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="8" x="-5.8" y="0.25" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="9" x="-5.8" y="-0.25" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="10" x="-5.8" y="-0.75" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="11" x="-5.8" y="-1.25" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="12" x="-5.8" y="-1.75" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="13" x="-5.8" y="-2.25" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="14" x="-5.8" y="-2.75" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="15" x="-5.8" y="-3.25" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="16" x="-5.8" y="-3.75" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="48" x="5.8" y="3.75" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="47" x="5.8" y="3.25" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="46" x="5.8" y="2.75" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="45" x="5.8" y="2.25" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="44" x="5.8" y="1.75" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="43" x="5.8" y="1.25" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="42" x="5.8" y="0.75" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="41" x="5.8" y="0.25" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="40" x="5.8" y="-0.25" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="39" x="5.8" y="-0.75" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="38" x="5.8" y="-1.25" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="37" x="5.8" y="-1.75" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="36" x="5.8" y="-2.25" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="35" x="5.8" y="-2.75" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="34" x="5.8" y="-3.25" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<smd name="33" x="5.8" y="-3.75" dx="0.3" dy="1.4" layer="1" rot="R90"/>
<text x="-3.54" y="-2.95" size="1.27" layer="27" ratio="10">&gt;VALUE</text>
<text x="-3.155" y="1.525" size="1.27" layer="25" ratio="10">&gt;NAME</text>
<rectangle x1="-3.89" y1="5.06" x2="-3.61" y2="6.03" layer="27"/>
<rectangle x1="-3.39" y1="5.06" x2="-3.11" y2="6.03" layer="27"/>
<rectangle x1="-2.89" y1="5.06" x2="-2.61" y2="6.03" layer="27"/>
<rectangle x1="-2.39" y1="5.06" x2="-2.11" y2="6.03" layer="27"/>
<rectangle x1="-1.89" y1="5.06" x2="-1.61" y2="6.03" layer="27"/>
<rectangle x1="-1.39" y1="5.06" x2="-1.11" y2="6.03" layer="27"/>
<rectangle x1="-0.89" y1="5.06" x2="-0.61" y2="6.03" layer="27"/>
<rectangle x1="-0.39" y1="5.06" x2="-0.11" y2="6.03" layer="27"/>
<rectangle x1="0.11" y1="5.06" x2="0.39" y2="6.03" layer="27"/>
<rectangle x1="0.61" y1="5.06" x2="0.89" y2="6.03" layer="27"/>
<rectangle x1="1.11" y1="5.06" x2="1.39" y2="6.03" layer="27"/>
<rectangle x1="1.61" y1="5.06" x2="1.89" y2="6.03" layer="27"/>
<rectangle x1="2.11" y1="5.06" x2="2.39" y2="6.03" layer="27"/>
<rectangle x1="2.61" y1="5.06" x2="2.89" y2="6.03" layer="27"/>
<rectangle x1="3.11" y1="5.06" x2="3.39" y2="6.03" layer="27"/>
<rectangle x1="3.61" y1="5.06" x2="3.89" y2="6.03" layer="27"/>
<rectangle x1="-3.89" y1="-6.03" x2="-3.61" y2="-5.06" layer="27"/>
<rectangle x1="-3.39" y1="-6.03" x2="-3.11" y2="-5.06" layer="27"/>
<rectangle x1="-2.89" y1="-6.03" x2="-2.61" y2="-5.06" layer="27"/>
<rectangle x1="-2.39" y1="-6.03" x2="-2.11" y2="-5.06" layer="27"/>
<rectangle x1="-1.89" y1="-6.03" x2="-1.61" y2="-5.06" layer="27"/>
<rectangle x1="-1.39" y1="-6.03" x2="-1.11" y2="-5.06" layer="27"/>
<rectangle x1="-0.89" y1="-6.03" x2="-0.61" y2="-5.06" layer="27"/>
<rectangle x1="-0.39" y1="-6.03" x2="-0.11" y2="-5.06" layer="27"/>
<rectangle x1="0.11" y1="-6.03" x2="0.39" y2="-5.06" layer="27"/>
<rectangle x1="0.61" y1="-6.03" x2="0.89" y2="-5.06" layer="27"/>
<rectangle x1="1.11" y1="-6.03" x2="1.39" y2="-5.06" layer="27"/>
<rectangle x1="1.61" y1="-6.03" x2="1.89" y2="-5.06" layer="27"/>
<rectangle x1="2.11" y1="-6.03" x2="2.39" y2="-5.06" layer="27"/>
<rectangle x1="2.61" y1="-6.03" x2="2.89" y2="-5.06" layer="27"/>
<rectangle x1="3.11" y1="-6.03" x2="3.39" y2="-5.06" layer="27"/>
<rectangle x1="3.61" y1="-6.03" x2="3.89" y2="-5.06" layer="27"/>
<rectangle x1="5.405" y1="3.265" x2="5.685" y2="4.235" layer="27" rot="R270"/>
<rectangle x1="5.405" y1="2.765" x2="5.685" y2="3.735" layer="27" rot="R270"/>
<rectangle x1="5.405" y1="2.265" x2="5.685" y2="3.235" layer="27" rot="R270"/>
<rectangle x1="5.405" y1="1.765" x2="5.685" y2="2.735" layer="27" rot="R270"/>
<rectangle x1="5.405" y1="1.265" x2="5.685" y2="2.235" layer="27" rot="R270"/>
<rectangle x1="5.405" y1="0.765" x2="5.685" y2="1.735" layer="27" rot="R270"/>
<rectangle x1="5.405" y1="0.265" x2="5.685" y2="1.235" layer="27" rot="R270"/>
<rectangle x1="5.405" y1="-0.235" x2="5.685" y2="0.735" layer="27" rot="R270"/>
<rectangle x1="5.405" y1="-0.735" x2="5.685" y2="0.235" layer="27" rot="R270"/>
<rectangle x1="5.405" y1="-1.235" x2="5.685" y2="-0.265" layer="27" rot="R270"/>
<rectangle x1="5.405" y1="-1.735" x2="5.685" y2="-0.765" layer="27" rot="R270"/>
<rectangle x1="5.405" y1="-2.235" x2="5.685" y2="-1.265" layer="27" rot="R270"/>
<rectangle x1="5.405" y1="-2.735" x2="5.685" y2="-1.765" layer="27" rot="R270"/>
<rectangle x1="5.405" y1="-3.235" x2="5.685" y2="-2.265" layer="27" rot="R270"/>
<rectangle x1="5.405" y1="-3.735" x2="5.685" y2="-2.765" layer="27" rot="R270"/>
<rectangle x1="5.405" y1="-4.235" x2="5.685" y2="-3.265" layer="27" rot="R270"/>
<rectangle x1="-5.685" y1="3.265" x2="-5.405" y2="4.235" layer="27" rot="R270"/>
<rectangle x1="-5.685" y1="2.765" x2="-5.405" y2="3.735" layer="27" rot="R270"/>
<rectangle x1="-5.685" y1="2.265" x2="-5.405" y2="3.235" layer="27" rot="R270"/>
<rectangle x1="-5.685" y1="1.765" x2="-5.405" y2="2.735" layer="27" rot="R270"/>
<rectangle x1="-5.685" y1="1.265" x2="-5.405" y2="2.235" layer="27" rot="R270"/>
<rectangle x1="-5.685" y1="0.765" x2="-5.405" y2="1.735" layer="27" rot="R270"/>
<rectangle x1="-5.685" y1="0.265" x2="-5.405" y2="1.235" layer="27" rot="R270"/>
<rectangle x1="-5.685" y1="-0.235" x2="-5.405" y2="0.735" layer="27" rot="R270"/>
<rectangle x1="-5.685" y1="-0.735" x2="-5.405" y2="0.235" layer="27" rot="R270"/>
<rectangle x1="-5.685" y1="-1.235" x2="-5.405" y2="-0.265" layer="27" rot="R270"/>
<rectangle x1="-5.685" y1="-1.735" x2="-5.405" y2="-0.765" layer="27" rot="R270"/>
<rectangle x1="-5.685" y1="-2.235" x2="-5.405" y2="-1.265" layer="27" rot="R270"/>
<rectangle x1="-5.685" y1="-2.735" x2="-5.405" y2="-1.765" layer="27" rot="R270"/>
<rectangle x1="-5.685" y1="-3.235" x2="-5.405" y2="-2.265" layer="27" rot="R270"/>
<rectangle x1="-5.685" y1="-3.735" x2="-5.405" y2="-2.765" layer="27" rot="R270"/>
<rectangle x1="-5.685" y1="-4.235" x2="-5.405" y2="-3.265" layer="27" rot="R270"/>
</package>
</packages>
<symbols>
<symbol name="F24X/F2410---PM64">
<wire x1="-35.56" y1="33.02" x2="38.1" y2="33.02" width="0.254" layer="94"/>
<wire x1="38.1" y1="33.02" x2="38.1" y2="-40.64" width="0.254" layer="94"/>
<wire x1="38.1" y1="-40.64" x2="-35.56" y2="-40.64" width="0.254" layer="94"/>
<wire x1="-35.56" y1="-40.64" x2="-35.56" y2="33.02" width="0.254" layer="94"/>
<circle x="-30.48" y="27.94" radius="1.27" width="0.254" layer="94"/>
<text x="-17.78" y="31.75" size="1.016" layer="95" font="vector" rot="MR270">AVcc</text>
<text x="-15.24" y="31.75" size="1.016" layer="95" font="vector" rot="MR270">DVss</text>
<text x="-12.7" y="31.75" size="1.016" layer="95" font="vector" rot="MR270">AVss</text>
<text x="-10.16" y="31.75" size="1.016" layer="95" font="vector" rot="MR270">P6.2/A2</text>
<text x="-7.62" y="31.75" size="1.016" layer="95" font="vector" rot="MR270">P6.1/A1</text>
<text x="-5.08" y="31.75" size="1.016" layer="95" font="vector" rot="MR270">P6.0/A0</text>
<text x="-2.54" y="31.75" size="1.016" layer="95" font="vector" rot="MR270">RST/NMI</text>
<text x="0" y="31.75" size="1.016" layer="95" font="vector" rot="MR270">TCK</text>
<text x="2.54" y="31.75" size="1.016" layer="95" font="vector" rot="MR270">TMS</text>
<text x="5.08" y="31.75" size="1.016" layer="95" font="vector" rot="MR270">TDI/TCLK</text>
<text x="7.62" y="31.75" size="1.016" layer="95" font="vector" rot="MR270">TDO/TDI</text>
<text x="10.16" y="31.75" size="1.016" layer="95" font="vector" rot="MR270">XT2IN</text>
<text x="12.7" y="31.75" size="1.016" layer="95" font="vector" rot="MR270">XT2OUT</text>
<text x="15.24" y="31.75" size="1.016" layer="95" font="vector" rot="MR270">P5.7/TBOUTH/SVSOUT</text>
<text x="17.78" y="31.75" size="1.016" layer="95" font="vector" rot="MR270">P5.6/ACLK</text>
<text x="20.32" y="31.75" size="1.016" layer="95" font="vector" rot="MR270">P5.5/SMCLK</text>
<text x="-34.29" y="15.24" size="1.016" layer="95" font="vector">DVcc</text>
<text x="-34.29" y="12.7" size="1.016" layer="95" font="vector">P6.3/A3</text>
<text x="-34.29" y="10.16" size="1.016" layer="95" font="vector">P6.4/A4</text>
<text x="-34.29" y="7.62" size="1.016" layer="95" font="vector">P6.5/A5</text>
<text x="-34.29" y="5.08" size="1.016" layer="95" font="vector">P6.6/A6</text>
<text x="-34.29" y="2.54" size="1.016" layer="95" font="vector">P6.7/A7/SVSIN</text>
<text x="-34.29" y="0" size="1.016" layer="95" font="vector">Vref+</text>
<text x="-34.29" y="-2.54" size="1.016" layer="95" font="vector">XIN</text>
<text x="-34.29" y="-5.08" size="1.016" layer="95" font="vector">XOUT</text>
<text x="-34.29" y="-7.62" size="1.016" layer="95" font="vector">Veref+</text>
<text x="-34.29" y="-10.16" size="1.016" layer="95" font="vector">Vref-/Veref-</text>
<text x="-34.29" y="-12.7" size="1.016" layer="95" font="vector">P1.0/TACLK/CAOUT</text>
<text x="-34.29" y="-15.24" size="1.016" layer="95" font="vector">P1.1/TA0</text>
<text x="-34.29" y="-17.78" size="1.016" layer="95" font="vector">P1.2/TA1</text>
<text x="-34.29" y="-20.32" size="1.016" layer="95" font="vector">P1.3/TA2</text>
<text x="-34.29" y="-22.86" size="1.016" layer="95" font="vector">P1.4/SMCLK</text>
<text x="-17.78" y="-39.37" size="1.016" layer="95" font="vector" rot="R90">P1.5/TA0</text>
<text x="-15.24" y="-39.37" size="1.016" layer="95" font="vector" rot="R90">P1.6/TA1</text>
<text x="-12.7" y="-39.37" size="1.016" layer="95" font="vector" rot="R90">P1.7/TA2</text>
<text x="-10.16" y="-39.37" size="1.016" layer="95" font="vector" rot="R90">P2.0/ACLK/CA2</text>
<text x="-7.62" y="-39.37" size="1.016" layer="95" font="vector" rot="R90">P2.1/TAINCLK/CA3</text>
<text x="-5.08" y="-39.37" size="1.016" layer="95" font="vector" rot="R90">P2.2/CAOUT/TA0/CA4</text>
<text x="-2.54" y="-39.37" size="1.016" layer="95" font="vector" rot="R90">P2.3/CA0/TA1</text>
<text x="0" y="-39.37" size="1.016" layer="95" font="vector" rot="R90">P2.4/CA1/TA2</text>
<text x="2.54" y="-39.37" size="1.016" layer="95" font="vector" rot="R90">P2.5/Rosc/CA5</text>
<text x="5.08" y="-39.37" size="1.016" layer="95" font="vector" rot="R90">P2.6/ADC12CLK/CA6</text>
<text x="7.62" y="-39.37" size="1.016" layer="95" font="vector" rot="R90">P2.7/TA0/CA7</text>
<text x="10.16" y="-39.37" size="1.016" layer="95" font="vector" rot="R90">P3.0/UCB0STE/...</text>
<text x="12.7" y="-39.37" size="1.016" layer="95" font="vector" rot="R90">P3.1/UCB0SIMO/...</text>
<text x="15.24" y="-39.37" size="1.016" layer="95" font="vector" rot="R90">P3.2/UCB0SOMI/...</text>
<text x="17.78" y="-39.37" size="1.016" layer="95" font="vector" rot="R90">P3.3/UCB0CLK/...</text>
<text x="20.32" y="-39.37" size="1.016" layer="95" font="vector" rot="R90">P3.4/UCA0TXD/...</text>
<text x="36.83" y="15.24" size="1.016" layer="95" font="vector" rot="MR0">P5.4/MCLK</text>
<text x="36.83" y="12.7" size="1.016" layer="95" font="vector" rot="MR0">P5.3/UCB1CLK/UCA1STE</text>
<text x="36.83" y="10.16" size="1.016" layer="95" font="vector" rot="MR0">P5.2/UCB1SOMI/UCB1SCL</text>
<text x="36.83" y="7.62" size="1.016" layer="95" font="vector" rot="MR0">P5.1/UCB1SIMO/UCB1SDA</text>
<text x="36.83" y="5.08" size="1.016" layer="95" font="vector" rot="MR0">P5.0/UCB1STE/UCA1CLK</text>
<text x="36.83" y="2.54" size="1.016" layer="95" font="vector" rot="MR0">P4.7/TBCLK</text>
<text x="36.83" y="0" size="1.016" layer="95" font="vector" rot="MR0">P4.6/TB6</text>
<text x="36.83" y="-2.54" size="1.016" layer="95" font="vector" rot="MR0">P4.5/TB5</text>
<text x="36.83" y="-5.08" size="1.016" layer="95" font="vector" rot="MR0">P4.4/TB4</text>
<text x="36.83" y="-7.62" size="1.016" layer="95" font="vector" rot="MR0">P4.3/TB3</text>
<text x="36.83" y="-10.16" size="1.016" layer="95" font="vector" rot="MR0">P4.2/TB2</text>
<text x="36.83" y="-12.7" size="1.016" layer="95" font="vector" rot="MR0">P4.1/TB1</text>
<text x="36.83" y="-15.24" size="1.016" layer="95" font="vector" rot="MR0">P4.0/TB0</text>
<text x="36.83" y="-17.78" size="1.016" layer="95" font="vector" rot="MR0">P3.7/UCA1RXD/UCA1SOMI</text>
<text x="36.83" y="-20.32" size="1.016" layer="95" font="vector" rot="MR0">P3.6/UCA1TXD/UCA1SIMO</text>
<text x="36.83" y="-22.86" size="1.016" layer="95" font="vector" rot="MR0">P3.5/UCA0RXD/UCA0SOMI</text>
<text x="-15.24" y="-5.08" size="3.81" layer="96" font="vector">MSP430F24x</text>
<text x="-7.62" y="10.16" size="3.81" layer="95" font="vector">&gt;NAME</text>
<text x="-15.24" y="-10.16" size="3.81" layer="96" font="vector">MSP430F2410</text>
<pin name="64" x="-17.78" y="38.1" visible="pad" length="middle" direction="pwr" rot="R270"/>
<pin name="63" x="-15.24" y="38.1" visible="pad" length="middle" direction="pwr" rot="R270"/>
<pin name="62" x="-12.7" y="38.1" visible="pad" length="middle" direction="pwr" rot="R270"/>
<pin name="61" x="-10.16" y="38.1" visible="pad" length="middle" rot="R270"/>
<pin name="60" x="-7.62" y="38.1" visible="pad" length="middle" rot="R270"/>
<pin name="59" x="-5.08" y="38.1" visible="pad" length="middle" rot="R270"/>
<pin name="58" x="-2.54" y="38.1" visible="pad" length="middle" direction="in" rot="R270"/>
<pin name="57" x="0" y="38.1" visible="pad" length="middle" direction="in" rot="R270"/>
<pin name="56" x="2.54" y="38.1" visible="pad" length="middle" direction="in" rot="R270"/>
<pin name="55" x="5.08" y="38.1" visible="pad" length="middle" direction="in" rot="R270"/>
<pin name="54" x="7.62" y="38.1" visible="pad" length="middle" rot="R270"/>
<pin name="53" x="10.16" y="38.1" visible="pad" length="middle" direction="in" rot="R270"/>
<pin name="52" x="12.7" y="38.1" visible="pad" length="middle" direction="out" rot="R270"/>
<pin name="51" x="15.24" y="38.1" visible="pad" length="middle" rot="R270"/>
<pin name="50" x="17.78" y="38.1" visible="pad" length="middle" rot="R270"/>
<pin name="49" x="20.32" y="38.1" visible="pad" length="middle" rot="R270"/>
<pin name="48" x="43.18" y="15.24" visible="pad" length="middle" rot="R180"/>
<pin name="47" x="43.18" y="12.7" visible="pad" length="middle" rot="R180"/>
<pin name="46" x="43.18" y="10.16" visible="pad" length="middle" rot="R180"/>
<pin name="45" x="43.18" y="7.62" visible="pad" length="middle" rot="R180"/>
<pin name="44" x="43.18" y="5.08" visible="pad" length="middle" rot="R180"/>
<pin name="43" x="43.18" y="2.54" visible="pad" length="middle" rot="R180"/>
<pin name="42" x="43.18" y="0" visible="pad" length="middle" rot="R180"/>
<pin name="41" x="43.18" y="-2.54" visible="pad" length="middle" rot="R180"/>
<pin name="40" x="43.18" y="-5.08" visible="pad" length="middle" rot="R180"/>
<pin name="39" x="43.18" y="-7.62" visible="pad" length="middle" rot="R180"/>
<pin name="38" x="43.18" y="-10.16" visible="pad" length="middle" rot="R180"/>
<pin name="37" x="43.18" y="-12.7" visible="pad" length="middle" rot="R180"/>
<pin name="36" x="43.18" y="-15.24" visible="pad" length="middle" rot="R180"/>
<pin name="35" x="43.18" y="-17.78" visible="pad" length="middle" rot="R180"/>
<pin name="34" x="43.18" y="-20.32" visible="pad" length="middle" rot="R180"/>
<pin name="33" x="43.18" y="-22.86" visible="pad" length="middle" rot="R180"/>
<pin name="32" x="20.32" y="-45.72" visible="pad" length="middle" rot="R90"/>
<pin name="31" x="17.78" y="-45.72" visible="pad" length="middle" rot="R90"/>
<pin name="30" x="15.24" y="-45.72" visible="pad" length="middle" rot="R90"/>
<pin name="29" x="12.7" y="-45.72" visible="pad" length="middle" rot="R90"/>
<pin name="28" x="10.16" y="-45.72" visible="pad" length="middle" rot="R90"/>
<pin name="27" x="7.62" y="-45.72" visible="pad" length="middle" rot="R90"/>
<pin name="26" x="5.08" y="-45.72" visible="pad" length="middle" rot="R90"/>
<pin name="25" x="2.54" y="-45.72" visible="pad" length="middle" rot="R90"/>
<pin name="24" x="0" y="-45.72" visible="pad" length="middle" rot="R90"/>
<pin name="23" x="-2.54" y="-45.72" visible="pad" length="middle" rot="R90"/>
<pin name="22" x="-5.08" y="-45.72" visible="pad" length="middle" rot="R90"/>
<pin name="21" x="-7.62" y="-45.72" visible="pad" length="middle" rot="R90"/>
<pin name="20" x="-10.16" y="-45.72" visible="pad" length="middle" rot="R90"/>
<pin name="19" x="-12.7" y="-45.72" visible="pad" length="middle" rot="R90"/>
<pin name="18" x="-15.24" y="-45.72" visible="pad" length="middle" rot="R90"/>
<pin name="17" x="-17.78" y="-45.72" visible="pad" length="middle" rot="R90"/>
<pin name="16" x="-40.64" y="-22.86" visible="pad" length="middle"/>
<pin name="1" x="-40.64" y="15.24" visible="pad" length="middle" direction="pwr"/>
<pin name="2" x="-40.64" y="12.7" visible="pad" length="middle"/>
<pin name="3" x="-40.64" y="10.16" visible="pad" length="middle"/>
<pin name="4" x="-40.64" y="7.62" visible="pad" length="middle"/>
<pin name="5" x="-40.64" y="5.08" visible="pad" length="middle"/>
<pin name="6" x="-40.64" y="2.54" visible="pad" length="middle"/>
<pin name="7" x="-40.64" y="0" visible="pad" length="middle" direction="out"/>
<pin name="8" x="-40.64" y="-2.54" visible="pad" length="middle" direction="in"/>
<pin name="9" x="-40.64" y="-5.08" visible="pad" length="middle" direction="out"/>
<pin name="11" x="-40.64" y="-10.16" visible="pad" length="middle" direction="in"/>
<pin name="12" x="-40.64" y="-12.7" visible="pad" length="middle"/>
<pin name="13" x="-40.64" y="-15.24" visible="pad" length="middle"/>
<pin name="14" x="-40.64" y="-17.78" visible="pad" length="middle"/>
<pin name="15" x="-40.64" y="-20.32" visible="pad" length="middle"/>
<pin name="10" x="-40.64" y="-7.62" visible="pad" length="middle" direction="out"/>
</symbol>
</symbols>
<devicesets>
<deviceset name="F24[X/10]---PM64">
<description>***MSP430F24[x/10]***PM64</description>
<gates>
<gate name="G$1" symbol="F24X/F2410---PM64" x="0" y="0"/>
</gates>
<devices>
<device name="" package="PM/PAG64">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="10" pad="10"/>
<connect gate="G$1" pin="11" pad="11"/>
<connect gate="G$1" pin="12" pad="12"/>
<connect gate="G$1" pin="13" pad="13"/>
<connect gate="G$1" pin="14" pad="14"/>
<connect gate="G$1" pin="15" pad="15"/>
<connect gate="G$1" pin="16" pad="16"/>
<connect gate="G$1" pin="17" pad="17"/>
<connect gate="G$1" pin="18" pad="18"/>
<connect gate="G$1" pin="19" pad="19"/>
<connect gate="G$1" pin="2" pad="2"/>
<connect gate="G$1" pin="20" pad="20"/>
<connect gate="G$1" pin="21" pad="21"/>
<connect gate="G$1" pin="22" pad="22"/>
<connect gate="G$1" pin="23" pad="23"/>
<connect gate="G$1" pin="24" pad="24"/>
<connect gate="G$1" pin="25" pad="25"/>
<connect gate="G$1" pin="26" pad="26"/>
<connect gate="G$1" pin="27" pad="27"/>
<connect gate="G$1" pin="28" pad="28"/>
<connect gate="G$1" pin="29" pad="29"/>
<connect gate="G$1" pin="3" pad="3"/>
<connect gate="G$1" pin="30" pad="30"/>
<connect gate="G$1" pin="31" pad="31"/>
<connect gate="G$1" pin="32" pad="32"/>
<connect gate="G$1" pin="33" pad="33"/>
<connect gate="G$1" pin="34" pad="34"/>
<connect gate="G$1" pin="35" pad="35"/>
<connect gate="G$1" pin="36" pad="36"/>
<connect gate="G$1" pin="37" pad="37"/>
<connect gate="G$1" pin="38" pad="38"/>
<connect gate="G$1" pin="39" pad="39"/>
<connect gate="G$1" pin="4" pad="4"/>
<connect gate="G$1" pin="40" pad="40"/>
<connect gate="G$1" pin="41" pad="41"/>
<connect gate="G$1" pin="42" pad="42"/>
<connect gate="G$1" pin="43" pad="43"/>
<connect gate="G$1" pin="44" pad="44"/>
<connect gate="G$1" pin="45" pad="45"/>
<connect gate="G$1" pin="46" pad="46"/>
<connect gate="G$1" pin="47" pad="47"/>
<connect gate="G$1" pin="48" pad="48"/>
<connect gate="G$1" pin="49" pad="49"/>
<connect gate="G$1" pin="5" pad="5"/>
<connect gate="G$1" pin="50" pad="50"/>
<connect gate="G$1" pin="51" pad="51"/>
<connect gate="G$1" pin="52" pad="52"/>
<connect gate="G$1" pin="53" pad="53"/>
<connect gate="G$1" pin="54" pad="54"/>
<connect gate="G$1" pin="55" pad="55"/>
<connect gate="G$1" pin="56" pad="56"/>
<connect gate="G$1" pin="57" pad="57"/>
<connect gate="G$1" pin="58" pad="58"/>
<connect gate="G$1" pin="59" pad="59"/>
<connect gate="G$1" pin="6" pad="6"/>
<connect gate="G$1" pin="60" pad="60"/>
<connect gate="G$1" pin="61" pad="61"/>
<connect gate="G$1" pin="62" pad="62"/>
<connect gate="G$1" pin="63" pad="63"/>
<connect gate="G$1" pin="64" pad="64"/>
<connect gate="G$1" pin="7" pad="7"/>
<connect gate="G$1" pin="8" pad="8"/>
<connect gate="G$1" pin="9" pad="9"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
<library name="SparkFun">
<description>&lt;h3&gt;SparkFun Electronics' preferred foot prints&lt;/h3&gt;
We've spent an enormous amount of time creating and checking these footprints and parts. If you enjoy using this library, please buy one of our products at www.sparkfun.com.
&lt;br&gt;&lt;br&gt;
&lt;b&gt;Licensing:&lt;/b&gt; CC v3.0 Share-Alike You are welcome to use this library for commercial purposes. For attribution, we ask that when you begin to sell your device using our footprint, you email us with a link to the product being sold. We want bragging rights that we helped (in a very small part) to create your 8th world wonder. We would like the opportunity to feature your device on our homepage.</description>
<packages>
</packages>
<symbols>
<symbol name="GND">
<wire x1="-1.905" y1="0" x2="1.905" y2="0" width="0.254" layer="94"/>
<text x="-2.54" y="-2.54" size="1.778" layer="96">&gt;VALUE</text>
<pin name="GND" x="0" y="2.54" visible="off" length="short" direction="sup" rot="R270"/>
</symbol>
</symbols>
<devicesets>
<deviceset name="GND" prefix="GND">
<description>&lt;b&gt;SUPPLY SYMBOL&lt;/b&gt;</description>
<gates>
<gate name="1" symbol="GND" x="0" y="0"/>
</gates>
<devices>
<device name="">
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
<library name="supply1">
<description>&lt;b&gt;Supply Symbols&lt;/b&gt;&lt;p&gt;
 GND, VCC, 0V, +5V, -5V, etc.&lt;p&gt;
 Please keep in mind, that these devices are necessary for the
 automatic wiring of the supply signals.&lt;p&gt;
 The pin name defined in the symbol is identical to the net which is to be wired automatically.&lt;p&gt;
 In this library the device names are the same as the pin names of the symbols, therefore the correct signal names appear next to the supply symbols in the schematic.&lt;p&gt;
 &lt;author&gt;Created by librarian@cadsoft.de&lt;/author&gt;</description>
<packages>
</packages>
<symbols>
<symbol name="+3V3">
<wire x1="1.27" y1="-1.905" x2="0" y2="0" width="0.254" layer="94"/>
<wire x1="0" y1="0" x2="-1.27" y2="-1.905" width="0.254" layer="94"/>
<text x="-2.54" y="-5.08" size="1.778" layer="96" rot="R90">&gt;VALUE</text>
<pin name="+3V3" x="0" y="-2.54" visible="off" length="short" direction="sup" rot="R90"/>
</symbol>
</symbols>
<devicesets>
<deviceset name="+3V3" prefix="+3V3">
<description>&lt;b&gt;SUPPLY SYMBOL&lt;/b&gt;</description>
<gates>
<gate name="G$1" symbol="+3V3" x="0" y="0"/>
</gates>
<devices>
<device name="">
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
<library name="SparkFun-Connectors">
<description>&lt;h3&gt;SparkFun Electronics' preferred foot prints&lt;/h3&gt;
In this library you'll find connectors and sockets- basically anything that can be plugged into or onto.&lt;br&gt;&lt;br&gt;
We've spent an enormous amount of time creating and checking these footprints and parts, but it is the end user's responsibility to ensure correctness and suitablity for a given componet or application. If you enjoy using this library, please buy one of our products at www.sparkfun.com.
&lt;br&gt;&lt;br&gt;
&lt;b&gt;Licensing:&lt;/b&gt; CC v3.0 Share-Alike You are welcome to use this library for commercial purposes. For attribution, we ask that when you begin to sell your device using our footprint, you email us with a link to the product being sold. We want bragging rights that we helped (in a very small part) to create your 8th world wonder. We would like the opportunity to feature your device on our homepage.</description>
<packages>
<package name="1X03">
<wire x1="3.81" y1="0.635" x2="4.445" y2="1.27" width="0.2032" layer="21"/>
<wire x1="4.445" y1="1.27" x2="5.715" y2="1.27" width="0.2032" layer="21"/>
<wire x1="5.715" y1="1.27" x2="6.35" y2="0.635" width="0.2032" layer="21"/>
<wire x1="6.35" y1="-0.635" x2="5.715" y2="-1.27" width="0.2032" layer="21"/>
<wire x1="5.715" y1="-1.27" x2="4.445" y2="-1.27" width="0.2032" layer="21"/>
<wire x1="4.445" y1="-1.27" x2="3.81" y2="-0.635" width="0.2032" layer="21"/>
<wire x1="-0.635" y1="1.27" x2="0.635" y2="1.27" width="0.2032" layer="21"/>
<wire x1="0.635" y1="1.27" x2="1.27" y2="0.635" width="0.2032" layer="21"/>
<wire x1="1.27" y1="-0.635" x2="0.635" y2="-1.27" width="0.2032" layer="21"/>
<wire x1="1.27" y1="0.635" x2="1.905" y2="1.27" width="0.2032" layer="21"/>
<wire x1="1.905" y1="1.27" x2="3.175" y2="1.27" width="0.2032" layer="21"/>
<wire x1="3.175" y1="1.27" x2="3.81" y2="0.635" width="0.2032" layer="21"/>
<wire x1="3.81" y1="-0.635" x2="3.175" y2="-1.27" width="0.2032" layer="21"/>
<wire x1="3.175" y1="-1.27" x2="1.905" y2="-1.27" width="0.2032" layer="21"/>
<wire x1="1.905" y1="-1.27" x2="1.27" y2="-0.635" width="0.2032" layer="21"/>
<wire x1="-1.27" y1="0.635" x2="-1.27" y2="-0.635" width="0.2032" layer="21"/>
<wire x1="-0.635" y1="1.27" x2="-1.27" y2="0.635" width="0.2032" layer="21"/>
<wire x1="-1.27" y1="-0.635" x2="-0.635" y2="-1.27" width="0.2032" layer="21"/>
<wire x1="0.635" y1="-1.27" x2="-0.635" y2="-1.27" width="0.2032" layer="21"/>
<wire x1="6.35" y1="0.635" x2="6.35" y2="-0.635" width="0.2032" layer="21"/>
<pad name="1" x="0" y="0" drill="1.016" diameter="1.8796" rot="R90"/>
<pad name="2" x="2.54" y="0" drill="1.016" diameter="1.8796" rot="R90"/>
<pad name="3" x="5.08" y="0" drill="1.016" diameter="1.8796" rot="R90"/>
<text x="-1.3462" y="1.8288" size="1.27" layer="25" ratio="10">&gt;NAME</text>
<text x="-1.27" y="-3.175" size="1.27" layer="27">&gt;VALUE</text>
<rectangle x1="4.826" y1="-0.254" x2="5.334" y2="0.254" layer="51"/>
<rectangle x1="2.286" y1="-0.254" x2="2.794" y2="0.254" layer="51"/>
<rectangle x1="-0.254" y1="-0.254" x2="0.254" y2="0.254" layer="51"/>
</package>
<package name="MOLEX-1X3">
<wire x1="-1.27" y1="3.048" x2="-1.27" y2="-2.54" width="0.127" layer="21"/>
<wire x1="6.35" y1="3.048" x2="6.35" y2="-2.54" width="0.127" layer="21"/>
<wire x1="6.35" y1="3.048" x2="-1.27" y2="3.048" width="0.127" layer="21"/>
<wire x1="6.35" y1="-2.54" x2="5.08" y2="-2.54" width="0.127" layer="21"/>
<wire x1="5.08" y1="-2.54" x2="0" y2="-2.54" width="0.127" layer="21"/>
<wire x1="0" y1="-2.54" x2="-1.27" y2="-2.54" width="0.127" layer="21"/>
<wire x1="0" y1="-2.54" x2="0" y2="-1.27" width="0.127" layer="21"/>
<wire x1="0" y1="-1.27" x2="5.08" y2="-1.27" width="0.127" layer="21"/>
<wire x1="5.08" y1="-1.27" x2="5.08" y2="-2.54" width="0.127" layer="21"/>
<pad name="1" x="0" y="0" drill="1.016" diameter="1.8796" shape="square"/>
<pad name="2" x="2.54" y="0" drill="1.016" diameter="1.8796"/>
<pad name="3" x="5.08" y="0" drill="1.016" diameter="1.8796"/>
</package>
<package name="SCREWTERMINAL-3.5MM-3">
<wire x1="-2.3" y1="3.4" x2="9.3" y2="3.4" width="0.2032" layer="21"/>
<wire x1="9.3" y1="3.4" x2="9.3" y2="-2.8" width="0.2032" layer="21"/>
<wire x1="9.3" y1="-2.8" x2="9.3" y2="-3.6" width="0.2032" layer="21"/>
<wire x1="9.3" y1="-3.6" x2="-2.3" y2="-3.6" width="0.2032" layer="21"/>
<wire x1="-2.3" y1="-3.6" x2="-2.3" y2="-2.8" width="0.2032" layer="21"/>
<wire x1="-2.3" y1="-2.8" x2="-2.3" y2="3.4" width="0.2032" layer="21"/>
<wire x1="9.3" y1="-2.8" x2="-2.3" y2="-2.8" width="0.2032" layer="21"/>
<wire x1="-2.3" y1="-1.35" x2="-2.7" y2="-1.35" width="0.2032" layer="51"/>
<wire x1="-2.7" y1="-1.35" x2="-2.7" y2="-2.35" width="0.2032" layer="51"/>
<wire x1="-2.7" y1="-2.35" x2="-2.3" y2="-2.35" width="0.2032" layer="51"/>
<wire x1="9.3" y1="3.15" x2="9.7" y2="3.15" width="0.2032" layer="51"/>
<wire x1="9.7" y1="3.15" x2="9.7" y2="2.15" width="0.2032" layer="51"/>
<wire x1="9.7" y1="2.15" x2="9.3" y2="2.15" width="0.2032" layer="51"/>
<pad name="1" x="0" y="0" drill="1.2" diameter="2.413" shape="square"/>
<pad name="2" x="3.5" y="0" drill="1.2" diameter="2.413"/>
<pad name="3" x="7" y="0" drill="1.2" diameter="2.413"/>
<text x="-1.27" y="2.54" size="0.4064" layer="25">&gt;NAME</text>
<text x="-1.27" y="1.27" size="0.4064" layer="27">&gt;VALUE</text>
</package>
<package name="1X03_LOCK">
<wire x1="3.81" y1="0.635" x2="4.445" y2="1.27" width="0.2032" layer="21"/>
<wire x1="4.445" y1="1.27" x2="5.715" y2="1.27" width="0.2032" layer="21"/>
<wire x1="5.715" y1="1.27" x2="6.35" y2="0.635" width="0.2032" layer="21"/>
<wire x1="6.35" y1="-0.635" x2="5.715" y2="-1.27" width="0.2032" layer="21"/>
<wire x1="5.715" y1="-1.27" x2="4.445" y2="-1.27" width="0.2032" layer="21"/>
<wire x1="4.445" y1="-1.27" x2="3.81" y2="-0.635" width="0.2032" layer="21"/>
<wire x1="-0.635" y1="1.27" x2="0.635" y2="1.27" width="0.2032" layer="21"/>
<wire x1="0.635" y1="1.27" x2="1.27" y2="0.635" width="0.2032" layer="21"/>
<wire x1="1.27" y1="-0.635" x2="0.635" y2="-1.27" width="0.2032" layer="21"/>
<wire x1="1.27" y1="0.635" x2="1.905" y2="1.27" width="0.2032" layer="21"/>
<wire x1="1.905" y1="1.27" x2="3.175" y2="1.27" width="0.2032" layer="21"/>
<wire x1="3.175" y1="1.27" x2="3.81" y2="0.635" width="0.2032" layer="21"/>
<wire x1="3.81" y1="-0.635" x2="3.175" y2="-1.27" width="0.2032" layer="21"/>
<wire x1="3.175" y1="-1.27" x2="1.905" y2="-1.27" width="0.2032" layer="21"/>
<wire x1="1.905" y1="-1.27" x2="1.27" y2="-0.635" width="0.2032" layer="21"/>
<wire x1="-1.27" y1="0.635" x2="-1.27" y2="-0.635" width="0.2032" layer="21"/>
<wire x1="-0.635" y1="1.27" x2="-1.27" y2="0.635" width="0.2032" layer="21"/>
<wire x1="-1.27" y1="-0.635" x2="-0.635" y2="-1.27" width="0.2032" layer="21"/>
<wire x1="0.635" y1="-1.27" x2="-0.635" y2="-1.27" width="0.2032" layer="21"/>
<wire x1="6.35" y1="0.635" x2="6.35" y2="-0.635" width="0.2032" layer="21"/>
<pad name="1" x="0" y="0.127" drill="1.016" diameter="1.8796" rot="R90"/>
<pad name="2" x="2.54" y="-0.127" drill="1.016" diameter="1.8796" rot="R90"/>
<pad name="3" x="5.08" y="0.127" drill="1.016" diameter="1.8796" rot="R90"/>
<text x="-1.3462" y="1.8288" size="1.27" layer="25" ratio="10">&gt;NAME</text>
<text x="-1.27" y="-3.175" size="1.27" layer="27">&gt;VALUE</text>
<rectangle x1="4.826" y1="-0.254" x2="5.334" y2="0.254" layer="51"/>
<rectangle x1="2.286" y1="-0.254" x2="2.794" y2="0.254" layer="51"/>
<rectangle x1="-0.254" y1="-0.254" x2="0.254" y2="0.254" layer="51"/>
</package>
<package name="1X03_LOCK_LONGPADS">
<description>This footprint was designed to help hold the alignment of a through-hole component (i.e.  6-pin header) while soldering it into place.  
You may notice that each hole has been shifted either up or down by 0.005 of an inch from it's more standard position (which is a perfectly straight line).  
This slight alteration caused the pins (the squares in the middle) to touch the edges of the holes.  Because they are alternating, it causes a "brace" 
to hold the component in place.  0.005 has proven to be the perfect amount of "off-center" position when using our standard breakaway headers.
Although looks a little odd when you look at the bare footprint, once you have a header in there, the alteration is very hard to notice.  Also,
if you push a header all the way into place, it is covered up entirely on the bottom side.  This idea of altering the position of holes to aid alignment 
will be further integrated into the Sparkfun Library for other footprints.  It can help hold any component with 3 or more connection pins.</description>
<wire x1="1.524" y1="-0.127" x2="1.016" y2="-0.127" width="0.2032" layer="21"/>
<wire x1="4.064" y1="-0.127" x2="3.556" y2="-0.127" width="0.2032" layer="21"/>
<wire x1="-1.27" y1="-0.127" x2="-1.016" y2="-0.127" width="0.2032" layer="21"/>
<wire x1="-1.27" y1="-0.127" x2="-1.27" y2="0.8636" width="0.2032" layer="21"/>
<wire x1="-1.27" y1="0.8636" x2="-0.9906" y2="1.143" width="0.2032" layer="21"/>
<wire x1="-1.27" y1="-0.127" x2="-1.27" y2="-1.1176" width="0.2032" layer="21"/>
<wire x1="-1.27" y1="-1.1176" x2="-0.9906" y2="-1.397" width="0.2032" layer="21"/>
<wire x1="6.35" y1="-0.127" x2="6.096" y2="-0.127" width="0.2032" layer="21"/>
<wire x1="6.35" y1="-0.127" x2="6.35" y2="-1.1176" width="0.2032" layer="21"/>
<wire x1="6.35" y1="-1.1176" x2="6.0706" y2="-1.397" width="0.2032" layer="21"/>
<wire x1="6.35" y1="-0.127" x2="6.35" y2="0.8636" width="0.2032" layer="21"/>
<wire x1="6.35" y1="0.8636" x2="6.0706" y2="1.143" width="0.2032" layer="21"/>
<pad name="1" x="0" y="0" drill="1.016" shape="long" rot="R90"/>
<pad name="2" x="2.54" y="-0.254" drill="1.016" shape="long" rot="R90"/>
<pad name="3" x="5.08" y="0" drill="1.016" shape="long" rot="R90"/>
<text x="-1.27" y="1.778" size="1.27" layer="25" font="vector">&gt;NAME</text>
<text x="-1.27" y="-3.302" size="1.27" layer="27" font="vector">&gt;VALUE</text>
<rectangle x1="-0.2921" y1="-0.4191" x2="0.2921" y2="0.1651" layer="51"/>
<rectangle x1="2.2479" y1="-0.4191" x2="2.8321" y2="0.1651" layer="51"/>
<rectangle x1="4.7879" y1="-0.4191" x2="5.3721" y2="0.1651" layer="51"/>
</package>
<package name="MOLEX-1X3_LOCK">
<wire x1="-1.27" y1="3.048" x2="-1.27" y2="-2.54" width="0.127" layer="21"/>
<wire x1="6.35" y1="3.048" x2="6.35" y2="-2.54" width="0.127" layer="21"/>
<wire x1="6.35" y1="3.048" x2="-1.27" y2="3.048" width="0.127" layer="21"/>
<wire x1="6.35" y1="-2.54" x2="5.08" y2="-2.54" width="0.127" layer="21"/>
<wire x1="5.08" y1="-2.54" x2="0" y2="-2.54" width="0.127" layer="21"/>
<wire x1="0" y1="-2.54" x2="-1.27" y2="-2.54" width="0.127" layer="21"/>
<wire x1="0" y1="-2.54" x2="0" y2="-1.27" width="0.127" layer="21"/>
<wire x1="0" y1="-1.27" x2="5.08" y2="-1.27" width="0.127" layer="21"/>
<wire x1="5.08" y1="-1.27" x2="5.08" y2="-2.54" width="0.127" layer="21"/>
<pad name="1" x="0" y="0.127" drill="1.016" diameter="1.8796" shape="square"/>
<pad name="2" x="2.54" y="-0.127" drill="1.016" diameter="1.8796"/>
<pad name="3" x="5.08" y="0.127" drill="1.016" diameter="1.8796"/>
<rectangle x1="-0.2921" y1="-0.2921" x2="0.2921" y2="0.2921" layer="51"/>
<rectangle x1="2.2479" y1="-0.2921" x2="2.8321" y2="0.2921" layer="51"/>
<rectangle x1="4.7879" y1="-0.2921" x2="5.3721" y2="0.2921" layer="51"/>
</package>
<package name="SCREWTERMINAL-3.5MM-3_LOCK.007S">
<wire x1="-2.3" y1="3.4" x2="9.3" y2="3.4" width="0.2032" layer="21"/>
<wire x1="9.3" y1="3.4" x2="9.3" y2="-2.8" width="0.2032" layer="21"/>
<wire x1="9.3" y1="-2.8" x2="9.3" y2="-3.6" width="0.2032" layer="21"/>
<wire x1="9.3" y1="-3.6" x2="-2.3" y2="-3.6" width="0.2032" layer="21"/>
<wire x1="-2.3" y1="-3.6" x2="-2.3" y2="-2.8" width="0.2032" layer="21"/>
<wire x1="-2.3" y1="-2.8" x2="-2.3" y2="3.4" width="0.2032" layer="21"/>
<wire x1="9.3" y1="-2.8" x2="-2.3" y2="-2.8" width="0.2032" layer="21"/>
<wire x1="-2.3" y1="-1.35" x2="-2.7" y2="-1.35" width="0.2032" layer="51"/>
<wire x1="-2.7" y1="-1.35" x2="-2.7" y2="-2.35" width="0.2032" layer="51"/>
<wire x1="-2.7" y1="-2.35" x2="-2.3" y2="-2.35" width="0.2032" layer="51"/>
<wire x1="9.3" y1="3.15" x2="9.7" y2="3.15" width="0.2032" layer="51"/>
<wire x1="9.7" y1="3.15" x2="9.7" y2="2.15" width="0.2032" layer="51"/>
<wire x1="9.7" y1="2.15" x2="9.3" y2="2.15" width="0.2032" layer="51"/>
<circle x="0" y="0" radius="0.425" width="0.001" layer="51"/>
<circle x="3.5" y="0" radius="0.425" width="0.001" layer="51"/>
<circle x="7" y="0" radius="0.425" width="0.001" layer="51"/>
<pad name="1" x="-0.1778" y="0" drill="1.2" diameter="2.032" shape="square"/>
<pad name="2" x="3.5" y="0" drill="1.2" diameter="2.032"/>
<pad name="3" x="7.1778" y="0" drill="1.2" diameter="2.032"/>
<text x="-1.27" y="2.54" size="0.4064" layer="25">&gt;NAME</text>
<text x="-1.27" y="1.27" size="0.4064" layer="27">&gt;VALUE</text>
</package>
<package name="1X03_NO_SILK">
<pad name="1" x="0" y="0" drill="1.016" diameter="1.8796" rot="R90"/>
<pad name="2" x="2.54" y="0" drill="1.016" diameter="1.8796" rot="R90"/>
<pad name="3" x="5.08" y="0" drill="1.016" diameter="1.8796" rot="R90"/>
<text x="-1.3462" y="1.8288" size="1.27" layer="25" ratio="10">&gt;NAME</text>
<text x="-1.27" y="-3.175" size="1.27" layer="27">&gt;VALUE</text>
<rectangle x1="4.826" y1="-0.254" x2="5.334" y2="0.254" layer="51"/>
<rectangle x1="2.286" y1="-0.254" x2="2.794" y2="0.254" layer="51"/>
<rectangle x1="-0.254" y1="-0.254" x2="0.254" y2="0.254" layer="51"/>
</package>
<package name="1X03_LONGPADS">
<wire x1="-1.27" y1="0.635" x2="-1.27" y2="-0.635" width="0.2032" layer="21"/>
<wire x1="6.35" y1="0.635" x2="6.35" y2="-0.635" width="0.2032" layer="21"/>
<pad name="1" x="0" y="0" drill="1.1176" diameter="1.8796" shape="long" rot="R90"/>
<pad name="2" x="2.54" y="0" drill="1.1176" diameter="1.8796" shape="long" rot="R90"/>
<pad name="3" x="5.08" y="0" drill="1.1176" diameter="1.8796" shape="long" rot="R90"/>
<text x="-1.3462" y="2.4638" size="1.27" layer="25" ratio="10">&gt;NAME</text>
<text x="-1.27" y="-3.81" size="1.27" layer="27">&gt;VALUE</text>
<rectangle x1="4.826" y1="-0.254" x2="5.334" y2="0.254" layer="51"/>
<rectangle x1="2.286" y1="-0.254" x2="2.794" y2="0.254" layer="51"/>
<rectangle x1="-0.254" y1="-0.254" x2="0.254" y2="0.254" layer="51"/>
</package>
<package name="JST-3-PTH">
<wire x1="-4" y1="-6.3" x2="-4" y2="1.5" width="0.2032" layer="21"/>
<wire x1="-4" y1="1.5" x2="4" y2="1.5" width="0.2032" layer="21"/>
<wire x1="4" y1="1.5" x2="4" y2="-6.3" width="0.2032" layer="21"/>
<wire x1="-4" y1="-6.3" x2="-3.3" y2="-6.3" width="0.2032" layer="21"/>
<wire x1="4" y1="-6.3" x2="3.3" y2="-6.3" width="0.2032" layer="21"/>
<wire x1="-3.3" y1="-6.3" x2="-3.3" y2="-5" width="0.2032" layer="21"/>
<wire x1="3.3" y1="-6.3" x2="3.3" y2="-5" width="0.2032" layer="21"/>
<pad name="1" x="-2" y="-5" drill="0.7" diameter="1.6256"/>
<pad name="2" x="0" y="-5" drill="0.7" diameter="1.6256"/>
<pad name="3" x="2" y="-5" drill="0.7" diameter="1.6256"/>
<text x="-1.27" y="0.24" size="0.4064" layer="25">&gt;Name</text>
<text x="-1.27" y="-1.03" size="0.4064" layer="27">&gt;Value</text>
<text x="-2.4" y="-4.33" size="1.27" layer="51">+</text>
<text x="-0.4" y="-4.33" size="1.27" layer="51">-</text>
<text x="1.7" y="-4.13" size="0.8" layer="51">S</text>
</package>
<package name="1X03_PP_HOLES_ONLY">
<circle x="0" y="0" radius="0.635" width="0.127" layer="51"/>
<circle x="2.54" y="0" radius="0.635" width="0.127" layer="51"/>
<circle x="5.08" y="0" radius="0.635" width="0.127" layer="51"/>
<pad name="1" x="0" y="0" drill="0.9" diameter="0.8128" rot="R90"/>
<pad name="2" x="2.54" y="0" drill="0.9" diameter="0.8128" rot="R90"/>
<pad name="3" x="5.08" y="0" drill="0.9" diameter="0.8128" rot="R90"/>
<hole x="0" y="0" drill="1.4732"/>
<hole x="2.54" y="0" drill="1.4732"/>
<hole x="5.08" y="0" drill="1.4732"/>
</package>
<package name="SCREWTERMINAL-5MM-3">
<wire x1="-3.1" y1="4.2" x2="13.1" y2="4.2" width="0.2032" layer="21"/>
<wire x1="13.1" y1="4.2" x2="13.1" y2="-2.3" width="0.2032" layer="21"/>
<wire x1="13.1" y1="-2.3" x2="13.1" y2="-3.3" width="0.2032" layer="21"/>
<wire x1="13.1" y1="-3.3" x2="-3.1" y2="-3.3" width="0.2032" layer="21"/>
<wire x1="-3.1" y1="-3.3" x2="-3.1" y2="-2.3" width="0.2032" layer="21"/>
<wire x1="-3.1" y1="-2.3" x2="-3.1" y2="4.2" width="0.2032" layer="21"/>
<wire x1="13.1" y1="-2.3" x2="-3.1" y2="-2.3" width="0.2032" layer="21"/>
<wire x1="-3.1" y1="-1.35" x2="-3.7" y2="-1.35" width="0.2032" layer="51"/>
<wire x1="-3.7" y1="-1.35" x2="-3.7" y2="-2.35" width="0.2032" layer="51"/>
<wire x1="-3.7" y1="-2.35" x2="-3.1" y2="-2.35" width="0.2032" layer="51"/>
<wire x1="13.1" y1="4" x2="13.7" y2="4" width="0.2032" layer="51"/>
<wire x1="13.7" y1="4" x2="13.7" y2="3" width="0.2032" layer="51"/>
<wire x1="13.7" y1="3" x2="13.1" y2="3" width="0.2032" layer="51"/>
<circle x="2.5" y="3.7" radius="0.2828" width="0.127" layer="51"/>
<pad name="1" x="0" y="0" drill="1.3" diameter="2.413" shape="square"/>
<pad name="2" x="5" y="0" drill="1.3" diameter="2.413"/>
<pad name="3" x="10" y="0" drill="1.3" diameter="2.413"/>
<text x="-1.27" y="2.54" size="0.4064" layer="25">&gt;NAME</text>
<text x="-1.27" y="1.27" size="0.4064" layer="27">&gt;VALUE</text>
</package>
<package name="1X03_LOCK_NO_SILK">
<pad name="1" x="0" y="0.127" drill="1.016" diameter="1.8796" rot="R90"/>
<pad name="2" x="2.54" y="-0.127" drill="1.016" diameter="1.8796" rot="R90"/>
<pad name="3" x="5.08" y="0.127" drill="1.016" diameter="1.8796" rot="R90"/>
<text x="-1.3462" y="1.8288" size="1.27" layer="25" ratio="10">&gt;NAME</text>
<text x="-1.27" y="-3.175" size="1.27" layer="27">&gt;VALUE</text>
<rectangle x1="4.826" y1="-0.254" x2="5.334" y2="0.254" layer="51"/>
<rectangle x1="2.286" y1="-0.254" x2="2.794" y2="0.254" layer="51"/>
<rectangle x1="-0.254" y1="-0.254" x2="0.254" y2="0.254" layer="51"/>
</package>
<package name="JST-3-SMD">
<wire x1="-4.99" y1="-2.07" x2="-4.99" y2="-5.57" width="0.2032" layer="21"/>
<wire x1="-4.99" y1="-5.57" x2="-4.19" y2="-5.57" width="0.2032" layer="21"/>
<wire x1="-4.19" y1="-5.57" x2="-4.19" y2="-3.07" width="0.2032" layer="21"/>
<wire x1="-4.19" y1="-3.07" x2="-2.99" y2="-3.07" width="0.2032" layer="21"/>
<wire x1="3.01" y1="-3.07" x2="4.21" y2="-3.07" width="0.2032" layer="21"/>
<wire x1="4.21" y1="-3.07" x2="4.21" y2="-5.57" width="0.2032" layer="21"/>
<wire x1="4.21" y1="-5.57" x2="5.01" y2="-5.57" width="0.2032" layer="21"/>
<wire x1="5.01" y1="-5.57" x2="5.01" y2="-2.07" width="0.2032" layer="21"/>
<wire x1="3.01" y1="1.93" x2="-2.99" y2="1.93" width="0.2032" layer="21"/>
<smd name="1" x="-1.99" y="-4.77" dx="1" dy="4.6" layer="1"/>
<smd name="3" x="2.01" y="-4.77" dx="1" dy="4.6" layer="1"/>
<smd name="NC1" x="-4.39" y="0.43" dx="3.4" dy="1.6" layer="1" rot="R90"/>
<smd name="NC2" x="4.41" y="0.43" dx="3.4" dy="1.6" layer="1" rot="R90"/>
<smd name="2" x="0.01" y="-4.77" dx="1" dy="4.6" layer="1"/>
<text x="-2.26" y="0.2" size="0.4064" layer="25">&gt;Name</text>
<text x="-2.26" y="-1.07" size="0.4064" layer="27">&gt;Value</text>
</package>
<package name="1X03-1MM-RA">
<wire x1="-1" y1="-4.6" x2="1" y2="-4.6" width="0.254" layer="21"/>
<wire x1="-2.5" y1="-2" x2="-2.5" y2="-0.35" width="0.254" layer="21"/>
<wire x1="1.75" y1="-0.35" x2="2.4997" y2="-0.35" width="0.254" layer="21"/>
<wire x1="2.4997" y1="-0.35" x2="2.4997" y2="-2" width="0.254" layer="21"/>
<wire x1="-2.5" y1="-0.35" x2="-1.75" y2="-0.35" width="0.254" layer="21"/>
<circle x="-2" y="0.3" radius="0.1414" width="0.4" layer="21"/>
<smd name="NC2" x="-2.3" y="-3.675" dx="1.2" dy="2" layer="1"/>
<smd name="NC1" x="2.3" y="-3.675" dx="1.2" dy="2" layer="1"/>
<smd name="1" x="-1" y="0" dx="0.6" dy="1.35" layer="1"/>
<smd name="2" x="0" y="0" dx="0.6" dy="1.35" layer="1"/>
<smd name="3" x="1" y="0" dx="0.6" dy="1.35" layer="1"/>
<text x="-1.73" y="1.73" size="0.4064" layer="25" rot="R180">&gt;NAME</text>
<text x="3.46" y="1.73" size="0.4064" layer="27" rot="R180">&gt;VALUE</text>
</package>
</packages>
<symbols>
<symbol name="M03">
<wire x1="3.81" y1="-5.08" x2="-2.54" y2="-5.08" width="0.4064" layer="94"/>
<wire x1="1.27" y1="2.54" x2="2.54" y2="2.54" width="0.6096" layer="94"/>
<wire x1="1.27" y1="0" x2="2.54" y2="0" width="0.6096" layer="94"/>
<wire x1="1.27" y1="-2.54" x2="2.54" y2="-2.54" width="0.6096" layer="94"/>
<wire x1="-2.54" y1="5.08" x2="-2.54" y2="-5.08" width="0.4064" layer="94"/>
<wire x1="3.81" y1="-5.08" x2="3.81" y2="5.08" width="0.4064" layer="94"/>
<wire x1="-2.54" y1="5.08" x2="3.81" y2="5.08" width="0.4064" layer="94"/>
<text x="-2.54" y="-7.62" size="1.778" layer="96">&gt;VALUE</text>
<text x="-2.54" y="5.842" size="1.778" layer="95">&gt;NAME</text>
<pin name="1" x="7.62" y="-2.54" visible="pad" length="middle" direction="pas" swaplevel="1" rot="R180"/>
<pin name="2" x="7.62" y="0" visible="pad" length="middle" direction="pas" swaplevel="1" rot="R180"/>
<pin name="3" x="7.62" y="2.54" visible="pad" length="middle" direction="pas" swaplevel="1" rot="R180"/>
</symbol>
</symbols>
<devicesets>
<deviceset name="M03" prefix="JP" uservalue="yes">
<description>&lt;b&gt;Header 3&lt;/b&gt;
Standard 3-pin 0.1" header. Use with straight break away headers (SKU : PRT-00116), right angle break away headers (PRT-00553), swiss pins (PRT-00743), machine pins (PRT-00117), and female headers (PRT-00115). Molex polarized connector foot print use with SKU : PRT-08232 with associated crimp pins and housings.</description>
<gates>
<gate name="G$1" symbol="M03" x="-2.54" y="0"/>
</gates>
<devices>
<device name="PTH" package="1X03">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
<connect gate="G$1" pin="3" pad="3"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="POLAR" package="MOLEX-1X3">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
<connect gate="G$1" pin="3" pad="3"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="SCREW" package="SCREWTERMINAL-3.5MM-3">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
<connect gate="G$1" pin="3" pad="3"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="LOCK" package="1X03_LOCK">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
<connect gate="G$1" pin="3" pad="3"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="LOCK_LONGPADS" package="1X03_LOCK_LONGPADS">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
<connect gate="G$1" pin="3" pad="3"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="POLAR_LOCK" package="MOLEX-1X3_LOCK">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
<connect gate="G$1" pin="3" pad="3"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="SCREW_LOCK" package="SCREWTERMINAL-3.5MM-3_LOCK.007S">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
<connect gate="G$1" pin="3" pad="3"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="1X03_NO_SILK" package="1X03_NO_SILK">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
<connect gate="G$1" pin="3" pad="3"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="LONGPADS" package="1X03_LONGPADS">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
<connect gate="G$1" pin="3" pad="3"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="JST-PTH" package="JST-3-PTH">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
<connect gate="G$1" pin="3" pad="3"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="POGO_PIN_HOLES_ONLY" package="1X03_PP_HOLES_ONLY">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
<connect gate="G$1" pin="3" pad="3"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="-SCREW-5MM" package="SCREWTERMINAL-5MM-3">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
<connect gate="G$1" pin="3" pad="3"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="LOCK_NO_SILK" package="1X03_LOCK_NO_SILK">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
<connect gate="G$1" pin="3" pad="3"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="" package="JST-3-SMD">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
<connect gate="G$1" pin="3" pad="3"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="SMD" package="1X03-1MM-RA">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
<connect gate="G$1" pin="3" pad="3"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
<library name="con-ml">
<description>&lt;b&gt;Harting  Connectors&lt;/b&gt;&lt;p&gt;
Low profile connectors, straight&lt;p&gt;
&lt;author&gt;Created by librarian@cadsoft.de&lt;/author&gt;</description>
<packages>
<package name="ML14">
<description>&lt;b&gt;HARTING&lt;/b&gt;</description>
<wire x1="-11.43" y1="3.175" x2="11.43" y2="3.175" width="0.127" layer="21"/>
<wire x1="11.43" y1="-3.175" x2="11.43" y2="3.175" width="0.127" layer="21"/>
<wire x1="-11.43" y1="3.175" x2="-11.43" y2="-3.175" width="0.127" layer="21"/>
<wire x1="-12.7" y1="4.445" x2="-11.43" y2="4.445" width="0.127" layer="21"/>
<wire x1="12.7" y1="-4.445" x2="8.001" y2="-4.445" width="0.127" layer="21"/>
<wire x1="12.7" y1="-4.445" x2="12.7" y2="4.445" width="0.127" layer="21"/>
<wire x1="-12.7" y1="4.445" x2="-12.7" y2="-4.445" width="0.127" layer="21"/>
<wire x1="11.43" y1="-3.175" x2="7.112" y2="-3.175" width="0.127" layer="21"/>
<wire x1="2.032" y1="-2.413" x2="-2.032" y2="-2.413" width="0.127" layer="21"/>
<wire x1="-2.032" y1="-3.175" x2="-2.032" y2="-2.413" width="0.127" layer="21"/>
<wire x1="-2.032" y1="-3.175" x2="-11.43" y2="-3.175" width="0.127" layer="21"/>
<wire x1="-2.032" y1="-3.175" x2="-2.032" y2="-3.429" width="0.127" layer="21"/>
<wire x1="2.032" y1="-2.413" x2="2.032" y2="-3.175" width="0.127" layer="21"/>
<wire x1="2.032" y1="-3.175" x2="2.032" y2="-3.429" width="0.127" layer="21"/>
<wire x1="11.43" y1="4.445" x2="11.43" y2="4.699" width="0.127" layer="21"/>
<wire x1="11.43" y1="4.699" x2="10.16" y2="4.699" width="0.127" layer="21"/>
<wire x1="10.16" y1="4.445" x2="10.16" y2="4.699" width="0.127" layer="21"/>
<wire x1="11.43" y1="4.445" x2="12.7" y2="4.445" width="0.127" layer="21"/>
<wire x1="0.635" y1="4.699" x2="-0.635" y2="4.699" width="0.127" layer="21"/>
<wire x1="0.635" y1="4.699" x2="0.635" y2="4.445" width="0.127" layer="21"/>
<wire x1="0.635" y1="4.445" x2="10.16" y2="4.445" width="0.127" layer="21"/>
<wire x1="-0.635" y1="4.699" x2="-0.635" y2="4.445" width="0.127" layer="21"/>
<wire x1="-10.16" y1="4.699" x2="-11.43" y2="4.699" width="0.127" layer="21"/>
<wire x1="-11.43" y1="4.699" x2="-11.43" y2="4.445" width="0.127" layer="21"/>
<wire x1="-10.16" y1="4.699" x2="-10.16" y2="4.445" width="0.127" layer="21"/>
<wire x1="-10.16" y1="4.445" x2="-0.635" y2="4.445" width="0.127" layer="21"/>
<wire x1="4.699" y1="-4.445" x2="2.032" y2="-4.445" width="0.127" layer="21"/>
<wire x1="2.032" y1="-4.445" x2="-2.032" y2="-4.445" width="0.127" layer="21"/>
<wire x1="5.588" y1="-3.175" x2="5.588" y2="-3.429" width="0.127" layer="21"/>
<wire x1="5.588" y1="-3.175" x2="2.032" y2="-3.175" width="0.127" layer="21"/>
<wire x1="7.112" y1="-3.175" x2="7.112" y2="-3.429" width="0.127" layer="21"/>
<wire x1="7.112" y1="-3.175" x2="5.588" y2="-3.175" width="0.127" layer="21"/>
<wire x1="4.699" y1="-4.445" x2="5.08" y2="-3.937" width="0.127" layer="21"/>
<wire x1="7.62" y1="-3.937" x2="8.001" y2="-4.445" width="0.127" layer="21"/>
<wire x1="7.62" y1="-3.937" x2="7.112" y2="-3.937" width="0.127" layer="21"/>
<wire x1="5.588" y1="-3.429" x2="2.032" y2="-3.429" width="0.0508" layer="21"/>
<wire x1="2.032" y1="-3.429" x2="2.032" y2="-4.445" width="0.127" layer="21"/>
<wire x1="7.112" y1="-3.429" x2="11.684" y2="-3.429" width="0.0508" layer="21"/>
<wire x1="11.684" y1="-3.429" x2="11.684" y2="3.429" width="0.0508" layer="21"/>
<wire x1="11.684" y1="3.429" x2="-11.684" y2="3.429" width="0.0508" layer="21"/>
<wire x1="-11.684" y1="3.429" x2="-11.684" y2="-3.429" width="0.0508" layer="21"/>
<wire x1="-11.684" y1="-3.429" x2="-2.032" y2="-3.429" width="0.0508" layer="21"/>
<wire x1="-2.032" y1="-3.429" x2="-2.032" y2="-4.445" width="0.127" layer="21"/>
<wire x1="5.588" y1="-3.429" x2="5.588" y2="-3.937" width="0.127" layer="21"/>
<wire x1="5.588" y1="-3.937" x2="5.08" y2="-3.937" width="0.127" layer="21"/>
<wire x1="7.112" y1="-3.429" x2="7.112" y2="-3.937" width="0.127" layer="21"/>
<wire x1="7.112" y1="-3.937" x2="5.588" y2="-3.937" width="0.127" layer="21"/>
<wire x1="-2.032" y1="-4.445" x2="-6.858" y2="-4.445" width="0.127" layer="21"/>
<wire x1="-6.858" y1="-4.318" x2="-6.858" y2="-4.445" width="0.127" layer="21"/>
<wire x1="-6.858" y1="-4.318" x2="-8.382" y2="-4.318" width="0.127" layer="21"/>
<wire x1="-8.382" y1="-4.445" x2="-8.382" y2="-4.318" width="0.127" layer="21"/>
<wire x1="-8.382" y1="-4.445" x2="-12.7" y2="-4.445" width="0.127" layer="21"/>
<pad name="1" x="-7.62" y="-1.27" drill="0.9144" shape="octagon"/>
<pad name="2" x="-7.62" y="1.27" drill="0.9144" shape="octagon"/>
<pad name="3" x="-5.08" y="-1.27" drill="0.9144" shape="octagon"/>
<pad name="4" x="-5.08" y="1.27" drill="0.9144" shape="octagon"/>
<pad name="5" x="-2.54" y="-1.27" drill="0.9144" shape="octagon"/>
<pad name="6" x="-2.54" y="1.27" drill="0.9144" shape="octagon"/>
<pad name="7" x="0" y="-1.27" drill="0.9144" shape="octagon"/>
<pad name="8" x="0" y="1.27" drill="0.9144" shape="octagon"/>
<pad name="9" x="2.54" y="-1.27" drill="0.9144" shape="octagon"/>
<pad name="10" x="2.54" y="1.27" drill="0.9144" shape="octagon"/>
<pad name="11" x="5.08" y="-1.27" drill="0.9144" shape="octagon"/>
<pad name="12" x="5.08" y="1.27" drill="0.9144" shape="octagon"/>
<pad name="13" x="7.62" y="-1.27" drill="0.9144" shape="octagon"/>
<pad name="14" x="7.62" y="1.27" drill="0.9144" shape="octagon"/>
<text x="-12.7" y="5.08" size="1.778" layer="25" ratio="10">&gt;NAME</text>
<text x="0" y="5.08" size="1.778" layer="27" ratio="10">&gt;VALUE</text>
<text x="-1.016" y="-4.064" size="1.27" layer="21" ratio="10">14</text>
<text x="-10.16" y="-1.905" size="1.27" layer="21" ratio="10">1</text>
<text x="-10.16" y="0.635" size="1.27" layer="21" ratio="10">2</text>
<rectangle x1="7.366" y1="1.016" x2="7.874" y2="1.524" layer="51"/>
<rectangle x1="4.826" y1="1.016" x2="5.334" y2="1.524" layer="51"/>
<rectangle x1="4.826" y1="-1.524" x2="5.334" y2="-1.016" layer="51"/>
<rectangle x1="7.366" y1="-1.524" x2="7.874" y2="-1.016" layer="51"/>
<rectangle x1="-5.334" y1="1.016" x2="-4.826" y2="1.524" layer="51"/>
<rectangle x1="-7.874" y1="1.016" x2="-7.366" y2="1.524" layer="51"/>
<rectangle x1="-2.794" y1="1.016" x2="-2.286" y2="1.524" layer="51"/>
<rectangle x1="2.286" y1="1.016" x2="2.794" y2="1.524" layer="51"/>
<rectangle x1="-0.254" y1="1.016" x2="0.254" y2="1.524" layer="51"/>
<rectangle x1="-5.334" y1="-1.524" x2="-4.826" y2="-1.016" layer="51"/>
<rectangle x1="-7.874" y1="-1.524" x2="-7.366" y2="-1.016" layer="51"/>
<rectangle x1="-2.794" y1="-1.524" x2="-2.286" y2="-1.016" layer="51"/>
<rectangle x1="2.286" y1="-1.524" x2="2.794" y2="-1.016" layer="51"/>
<rectangle x1="-0.254" y1="-1.524" x2="0.254" y2="-1.016" layer="51"/>
</package>
</packages>
<symbols>
<symbol name="14P">
<wire x1="3.81" y1="-10.16" x2="-3.81" y2="-10.16" width="0.4064" layer="94"/>
<wire x1="-3.81" y1="10.16" x2="-3.81" y2="-10.16" width="0.4064" layer="94"/>
<wire x1="-3.81" y1="10.16" x2="3.81" y2="10.16" width="0.4064" layer="94"/>
<wire x1="3.81" y1="-10.16" x2="3.81" y2="10.16" width="0.4064" layer="94"/>
<wire x1="2.54" y1="5.08" x2="3.175" y2="5.08" width="0.1524" layer="94"/>
<wire x1="1.27" y1="2.54" x2="2.54" y2="2.54" width="0.6096" layer="94"/>
<wire x1="1.27" y1="0" x2="2.54" y2="0" width="0.6096" layer="94"/>
<wire x1="1.27" y1="-2.54" x2="2.54" y2="-2.54" width="0.6096" layer="94"/>
<wire x1="1.27" y1="-5.08" x2="2.54" y2="-5.08" width="0.6096" layer="94"/>
<wire x1="1.27" y1="-7.62" x2="2.54" y2="-7.62" width="0.6096" layer="94"/>
<wire x1="-2.54" y1="2.54" x2="-1.27" y2="2.54" width="0.6096" layer="94"/>
<wire x1="-2.54" y1="0" x2="-1.27" y2="0" width="0.6096" layer="94"/>
<wire x1="-2.54" y1="-2.54" x2="-1.27" y2="-2.54" width="0.6096" layer="94"/>
<wire x1="-2.54" y1="-5.08" x2="-1.27" y2="-5.08" width="0.6096" layer="94"/>
<wire x1="-2.54" y1="-7.62" x2="-1.27" y2="-7.62" width="0.6096" layer="94"/>
<wire x1="1.27" y1="5.08" x2="2.54" y2="5.08" width="0.6096" layer="94"/>
<wire x1="1.27" y1="7.62" x2="2.54" y2="7.62" width="0.6096" layer="94"/>
<wire x1="-2.54" y1="5.08" x2="-1.27" y2="5.08" width="0.6096" layer="94"/>
<wire x1="-2.54" y1="7.62" x2="-1.27" y2="7.62" width="0.6096" layer="94"/>
<text x="-3.81" y="-12.7" size="1.778" layer="96">&gt;VALUE</text>
<text x="-3.81" y="10.922" size="1.778" layer="95">&gt;NAME</text>
<pin name="1" x="7.62" y="-7.62" visible="pad" length="middle" direction="pas" rot="R180"/>
<pin name="3" x="7.62" y="-5.08" visible="pad" length="middle" direction="pas" rot="R180"/>
<pin name="5" x="7.62" y="-2.54" visible="pad" length="middle" direction="pas" rot="R180"/>
<pin name="7" x="7.62" y="0" visible="pad" length="middle" direction="pas" rot="R180"/>
<pin name="9" x="7.62" y="2.54" visible="pad" length="middle" direction="pas" rot="R180"/>
<pin name="11" x="7.62" y="5.08" visible="pad" length="middle" direction="pas" rot="R180"/>
<pin name="13" x="7.62" y="7.62" visible="pad" length="middle" direction="pas" rot="R180"/>
<pin name="2" x="-7.62" y="-7.62" visible="pad" length="middle" direction="pas"/>
<pin name="4" x="-7.62" y="-5.08" visible="pad" length="middle" direction="pas"/>
<pin name="6" x="-7.62" y="-2.54" visible="pad" length="middle" direction="pas"/>
<pin name="12" x="-7.62" y="5.08" visible="pad" length="middle" direction="pas"/>
<pin name="14" x="-7.62" y="7.62" visible="pad" length="middle" direction="pas"/>
<pin name="8" x="-7.62" y="0" visible="pad" length="middle" direction="pas"/>
<pin name="10" x="-7.62" y="2.54" visible="pad" length="middle" direction="pas"/>
</symbol>
</symbols>
<devicesets>
<deviceset name="ML14" prefix="SV" uservalue="yes">
<description>&lt;b&gt;HARTING&lt;/b&gt;</description>
<gates>
<gate name="1" symbol="14P" x="0" y="0"/>
</gates>
<devices>
<device name="" package="ML14">
<connects>
<connect gate="1" pin="1" pad="1"/>
<connect gate="1" pin="10" pad="10"/>
<connect gate="1" pin="11" pad="11"/>
<connect gate="1" pin="12" pad="12"/>
<connect gate="1" pin="13" pad="13"/>
<connect gate="1" pin="14" pad="14"/>
<connect gate="1" pin="2" pad="2"/>
<connect gate="1" pin="3" pad="3"/>
<connect gate="1" pin="4" pad="4"/>
<connect gate="1" pin="5" pad="5"/>
<connect gate="1" pin="6" pad="6"/>
<connect gate="1" pin="7" pad="7"/>
<connect gate="1" pin="8" pad="8"/>
<connect gate="1" pin="9" pad="9"/>
</connects>
<technologies>
<technology name="">
<attribute name="MF" value="" constant="no"/>
<attribute name="MPN" value="" constant="no"/>
<attribute name="OC_FARNELL" value="unknown" constant="no"/>
<attribute name="OC_NEWARK" value="unknown" constant="no"/>
</technology>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
</libraries>
<attributes>
</attributes>
<variantdefs>
</variantdefs>
<classes>
<class number="0" name="default" width="0" drill="0">
</class>
</classes>
<parts>
<part name="U$1" library="TI_MSP430_v16" deviceset="F24[X/10]---PM64" device=""/>
<part name="GND2" library="SparkFun" deviceset="GND" device=""/>
<part name="+3V1" library="supply1" deviceset="+3V3" device=""/>
<part name="SV3" library="con-ml" deviceset="ML14" device="" value="14 PIN JTAG"/>
<part name="+3V8" library="supply1" deviceset="+3V3" device=""/>
<part name="GND35" library="SparkFun" deviceset="GND" device=""/>
<part name="JP18" library="SparkFun-Connectors" deviceset="M03" device="SCREW" value="VRAILS"/>
</parts>
<sheets>
<sheet>
<plain>
</plain>
<instances>
<instance part="U$1" gate="G$1" x="119.38" y="63.5"/>
<instance part="GND2" gate="1" x="104.14" y="116.84" rot="R180"/>
<instance part="+3V1" gate="G$1" x="76.2" y="88.9" smashed="yes"/>
<instance part="SV3" gate="1" x="118.11" y="139.7" smashed="yes">
<attribute name="VALUE" x="110.49" y="127" size="1.778" layer="96"/>
<attribute name="NAME" x="114.3" y="150.622" size="1.778" layer="95"/>
</instance>
<instance part="+3V8" gate="G$1" x="101.6" y="111.76" smashed="yes"/>
<instance part="GND35" gate="1" x="109.22" y="111.76" rot="R180"/>
<instance part="JP18" gate="G$1" x="64.77" y="129.54"/>
</instances>
<busses>
</busses>
<nets>
<net name="GND" class="0">
<segment>
<pinref part="U$1" gate="G$1" pin="63"/>
<wire x1="104.14" y1="101.6" x2="104.14" y2="114.3" width="0.127" layer="91"/>
<pinref part="GND2" gate="1" pin="GND"/>
</segment>
<segment>
<pinref part="SV3" gate="1" pin="9"/>
<wire x1="125.73" y1="142.24" x2="130.81" y2="142.24" width="0.1524" layer="91"/>
<label x="130.81" y="142.24" size="1.778" layer="95"/>
</segment>
<segment>
<pinref part="U$1" gate="G$1" pin="62"/>
<wire x1="106.68" y1="101.6" x2="106.68" y2="106.68" width="0.1524" layer="91"/>
<wire x1="106.68" y1="106.68" x2="109.22" y2="106.68" width="0.1524" layer="91"/>
<pinref part="GND35" gate="1" pin="GND"/>
<wire x1="109.22" y1="106.68" x2="109.22" y2="109.22" width="0.1524" layer="91"/>
</segment>
<segment>
<pinref part="JP18" gate="G$1" pin="1"/>
<wire x1="72.39" y1="127" x2="77.47" y2="127" width="0.1524" layer="91"/>
<label x="77.47" y="127" size="1.778" layer="95"/>
</segment>
</net>
<net name="+12V" class="0">
<segment>
<pinref part="JP18" gate="G$1" pin="3"/>
<wire x1="72.39" y1="132.08" x2="77.47" y2="132.08" width="0.1524" layer="91"/>
<label x="77.47" y="132.08" size="1.778" layer="95"/>
</segment>
</net>
<net name="+3V3" class="0">
<segment>
<pinref part="U$1" gate="G$1" pin="1"/>
<wire x1="78.74" y1="78.74" x2="76.2" y2="78.74" width="0.1524" layer="91"/>
<pinref part="+3V1" gate="G$1" pin="+3V3"/>
<wire x1="76.2" y1="78.74" x2="76.2" y2="86.36" width="0.1524" layer="91"/>
<label x="76.2" y="88.9" size="1.778" layer="95"/>
</segment>
<segment>
<pinref part="SV3" gate="1" pin="2"/>
<wire x1="110.49" y1="132.08" x2="105.41" y2="132.08" width="0.1524" layer="91"/>
<label x="100.33" y="132.08" size="1.778" layer="95"/>
</segment>
<segment>
<pinref part="U$1" gate="G$1" pin="64"/>
<wire x1="101.6" y1="101.6" x2="101.6" y2="109.22" width="0.1524" layer="91"/>
<pinref part="+3V8" gate="G$1" pin="+3V3"/>
<label x="99.06" y="109.22" size="1.778" layer="95" rot="R90"/>
</segment>
<segment>
<pinref part="JP18" gate="G$1" pin="2"/>
<wire x1="72.39" y1="129.54" x2="77.47" y2="129.54" width="0.1524" layer="91"/>
<label x="77.47" y="129.54" size="1.778" layer="95"/>
</segment>
</net>
<net name="TDO" class="0">
<segment>
<pinref part="SV3" gate="1" pin="1"/>
<wire x1="125.73" y1="132.08" x2="130.81" y2="132.08" width="0.1524" layer="91"/>
<label x="130.81" y="132.08" size="1.778" layer="95"/>
</segment>
<segment>
<pinref part="U$1" gate="G$1" pin="54"/>
<wire x1="127" y1="101.6" x2="127" y2="106.68" width="0.1524" layer="91"/>
<label x="127" y="106.68" size="1.778" layer="95" rot="R90"/>
</segment>
</net>
<net name="TCK" class="0">
<segment>
<pinref part="SV3" gate="1" pin="7"/>
<wire x1="125.73" y1="139.7" x2="130.81" y2="139.7" width="0.1524" layer="91"/>
<label x="130.81" y="139.7" size="1.778" layer="95"/>
</segment>
<segment>
<pinref part="U$1" gate="G$1" pin="57"/>
<wire x1="119.38" y1="101.6" x2="119.38" y2="106.68" width="0.1524" layer="91"/>
<label x="119.38" y="106.68" size="1.778" layer="95" rot="R90"/>
</segment>
</net>
<net name="RST/NMI" class="0">
<segment>
<pinref part="SV3" gate="1" pin="11"/>
<wire x1="125.73" y1="144.78" x2="130.81" y2="144.78" width="0.1524" layer="91"/>
<label x="130.81" y="144.78" size="1.778" layer="95"/>
</segment>
<segment>
<pinref part="U$1" gate="G$1" pin="58"/>
<wire x1="116.84" y1="101.6" x2="116.84" y2="106.68" width="0.1524" layer="91"/>
<label x="116.84" y="106.68" size="1.778" layer="95" rot="R90"/>
</segment>
</net>
<net name="TMS" class="0">
<segment>
<pinref part="U$1" gate="G$1" pin="56"/>
<wire x1="121.92" y1="101.6" x2="121.92" y2="106.68" width="0.1524" layer="91"/>
<label x="121.92" y="106.68" size="1.778" layer="95" rot="R90"/>
</segment>
<segment>
<pinref part="SV3" gate="1" pin="5"/>
<wire x1="125.73" y1="137.16" x2="130.81" y2="137.16" width="0.1524" layer="91"/>
<label x="130.81" y="137.16" size="1.778" layer="95"/>
</segment>
</net>
<net name="TDI" class="0">
<segment>
<pinref part="U$1" gate="G$1" pin="55"/>
<wire x1="124.46" y1="101.6" x2="124.46" y2="106.68" width="0.1524" layer="91"/>
<label x="124.46" y="106.68" size="1.778" layer="95" rot="R90"/>
</segment>
<segment>
<pinref part="SV3" gate="1" pin="3"/>
<wire x1="125.73" y1="134.62" x2="130.81" y2="134.62" width="0.1524" layer="91"/>
<label x="130.81" y="134.62" size="1.778" layer="95"/>
</segment>
</net>
</nets>
</sheet>
</sheets>
<errors>
<approved hash="104,1,101.6,101.6,U$1,64,+3V3,,,"/>
<approved hash="104,1,104.14,101.6,U$1,63,GND,,,"/>
<approved hash="104,1,106.68,101.6,U$1,62,GND,,,"/>
<approved hash="202,1,129.54,101.6,U$1,53,,,,"/>
<approved hash="104,1,78.74,78.74,U$1,1,+3V3,,,"/>
<approved hash="202,1,78.74,53.34,U$1,11,,,,"/>
</errors>
</schematic>
</drawing>
</eagle>
