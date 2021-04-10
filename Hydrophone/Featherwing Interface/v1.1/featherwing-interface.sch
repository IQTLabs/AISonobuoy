<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE eagle SYSTEM "eagle.dtd">
<eagle version="9.6.2">
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
<layer number="21" name="tPlace" color="14" fill="1" visible="no" active="no"/>
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
<layer number="57" name="tCAD" color="7" fill="1" visible="no" active="no"/>
<layer number="59" name="tCarbon" color="7" fill="1" visible="no" active="no"/>
<layer number="60" name="bCarbon" color="7" fill="1" visible="no" active="no"/>
<layer number="88" name="SimResults" color="9" fill="1" visible="yes" active="yes"/>
<layer number="89" name="SimProbes" color="9" fill="1" visible="yes" active="yes"/>
<layer number="90" name="Modules" color="5" fill="1" visible="yes" active="yes"/>
<layer number="91" name="Nets" color="2" fill="1" visible="yes" active="yes"/>
<layer number="92" name="Busses" color="1" fill="1" visible="yes" active="yes"/>
<layer number="93" name="Pins" color="2" fill="1" visible="no" active="yes"/>
<layer number="94" name="Symbols" color="4" fill="1" visible="yes" active="yes"/>
<layer number="95" name="Names" color="7" fill="1" visible="yes" active="yes"/>
<layer number="96" name="Values" color="7" fill="1" visible="yes" active="yes"/>
<layer number="97" name="Info" color="7" fill="1" visible="yes" active="yes"/>
<layer number="98" name="Guide" color="6" fill="1" visible="yes" active="yes"/>
<layer number="99" name="SpiceOrder" color="7" fill="1" visible="no" active="no"/>
<layer number="100" name="Muster" color="7" fill="1" visible="yes" active="yes"/>
<layer number="101" name="Patch_Top" color="12" fill="4" visible="yes" active="yes"/>
<layer number="102" name="Mittellin" color="7" fill="1" visible="yes" active="yes"/>
<layer number="103" name="Stiffner" color="7" fill="1" visible="yes" active="yes"/>
<layer number="104" name="Name" color="7" fill="1" visible="yes" active="yes"/>
<layer number="105" name="Beschreib" color="7" fill="1" visible="yes" active="yes"/>
<layer number="106" name="BGA-Top" color="7" fill="1" visible="yes" active="yes"/>
<layer number="107" name="BD-Top" color="7" fill="1" visible="yes" active="yes"/>
<layer number="108" name="tBridges" color="7" fill="1" visible="yes" active="yes"/>
<layer number="109" name="tBPL" color="7" fill="1" visible="yes" active="yes"/>
<layer number="110" name="bBPL" color="7" fill="1" visible="yes" active="yes"/>
<layer number="111" name="MPL" color="7" fill="1" visible="yes" active="yes"/>
<layer number="112" name="tSilk" color="7" fill="1" visible="yes" active="yes"/>
<layer number="113" name="ReferenceLS" color="7" fill="1" visible="no" active="no"/>
<layer number="116" name="Patch_BOT" color="9" fill="4" visible="yes" active="yes"/>
<layer number="118" name="Rect_Pads" color="7" fill="1" visible="no" active="no"/>
<layer number="121" name="sName" color="7" fill="1" visible="yes" active="yes"/>
<layer number="122" name="_bPlace" color="7" fill="1" visible="yes" active="yes"/>
<layer number="123" name="tTestmark" color="7" fill="1" visible="no" active="yes"/>
<layer number="124" name="bTestmark" color="7" fill="1" visible="no" active="yes"/>
<layer number="125" name="_tNames" color="7" fill="1" visible="yes" active="yes"/>
<layer number="126" name="_bNames" color="7" fill="1" visible="yes" active="yes"/>
<layer number="127" name="_tValues" color="7" fill="1" visible="yes" active="yes"/>
<layer number="128" name="_bValues" color="7" fill="1" visible="yes" active="yes"/>
<layer number="129" name="Mask" color="7" fill="1" visible="yes" active="yes"/>
<layer number="131" name="tAdjust" color="7" fill="1" visible="no" active="yes"/>
<layer number="132" name="bAdjust" color="7" fill="1" visible="no" active="yes"/>
<layer number="144" name="Drill_legend" color="7" fill="1" visible="yes" active="yes"/>
<layer number="150" name="Notes" color="7" fill="1" visible="no" active="yes"/>
<layer number="151" name="HeatSink" color="7" fill="1" visible="yes" active="yes"/>
<layer number="152" name="_bDocu" color="7" fill="1" visible="yes" active="yes"/>
<layer number="153" name="FabDoc1" color="6" fill="1" visible="no" active="no"/>
<layer number="154" name="FabDoc2" color="2" fill="1" visible="no" active="no"/>
<layer number="155" name="FabDoc3" color="7" fill="15" visible="no" active="no"/>
<layer number="199" name="Contour" color="7" fill="1" visible="yes" active="yes"/>
<layer number="200" name="200bmp" color="1" fill="10" visible="yes" active="yes"/>
<layer number="201" name="201bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="202" name="202bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="203" name="203bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="204" name="204bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="205" name="205bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="206" name="206bmp" color="7" fill="10" visible="yes" active="yes"/>
<layer number="207" name="207bmp" color="8" fill="10" visible="yes" active="yes"/>
<layer number="208" name="208bmp" color="9" fill="10" visible="yes" active="yes"/>
<layer number="209" name="209bmp" color="7" fill="1" visible="no" active="yes"/>
<layer number="210" name="210bmp" color="7" fill="1" visible="no" active="yes"/>
<layer number="211" name="211bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="212" name="212bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="213" name="213bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="214" name="214bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="215" name="215bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="216" name="216bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="217" name="217bmp" color="18" fill="1" visible="no" active="no"/>
<layer number="218" name="218bmp" color="19" fill="1" visible="no" active="no"/>
<layer number="219" name="219bmp" color="20" fill="1" visible="no" active="no"/>
<layer number="220" name="220bmp" color="21" fill="1" visible="no" active="no"/>
<layer number="221" name="221bmp" color="22" fill="1" visible="no" active="no"/>
<layer number="222" name="222bmp" color="23" fill="1" visible="no" active="no"/>
<layer number="223" name="223bmp" color="24" fill="1" visible="no" active="no"/>
<layer number="224" name="224bmp" color="25" fill="1" visible="no" active="no"/>
<layer number="225" name="225bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="226" name="226bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="227" name="227bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="228" name="228bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="229" name="229bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="230" name="230bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="231" name="Eagle3D_PG1" color="7" fill="1" visible="no" active="no"/>
<layer number="232" name="Eagle3D_PG2" color="7" fill="1" visible="no" active="no"/>
<layer number="233" name="Eagle3D_PG3" color="7" fill="1" visible="no" active="no"/>
<layer number="248" name="Housing" color="7" fill="1" visible="yes" active="yes"/>
<layer number="249" name="Edge" color="7" fill="1" visible="yes" active="yes"/>
<layer number="250" name="Descript" color="7" fill="1" visible="yes" active="yes"/>
<layer number="251" name="SMDround" color="7" fill="1" visible="yes" active="yes"/>
<layer number="254" name="cooling" color="7" fill="1" visible="yes" active="yes"/>
<layer number="255" name="routoute" color="7" fill="1" visible="yes" active="yes"/>
</layers>
<schematic xreflabel="%F%N/%S.%C%R" xrefpart="/%S.%C%R">
<libraries>
<library name="microbuilder">
<description>&lt;h2&gt;&lt;b&gt;microBuilder.eu&lt;/b&gt; Eagle Footprint Library&lt;/h2&gt;

&lt;p&gt;Footprints for common components used in our projects and products.  This is the same library that we use internally, and it is regularly updated.  The newest version can always be found at &lt;b&gt;www.microBuilder.eu&lt;/b&gt;.  If you find this library useful, please feel free to purchase something from our online store. Please also note that all holes are optimised for metric drill bits!&lt;/p&gt;

&lt;h3&gt;Obligatory Warning&lt;/h3&gt;
&lt;p&gt;While it probably goes without saying, there are no guarantees that the footprints or schematic symbols in this library are flawless, and we make no promises of fitness for production, prototyping or any other purpose. These libraries are provided for information puposes only, and are used at your own discretion.  While we make every effort to produce accurate footprints, and many of the items found in this library have be proven in production, we can't make any promises of suitability for a specific purpose. If you do find any errors, though, please feel free to contact us at www.microbuilder.eu to let us know about it so that we can update the library accordingly!&lt;/p&gt;

&lt;h3&gt;License&lt;/h3&gt;
&lt;p&gt;This work is placed in the public domain, and may be freely used for commercial and non-commercial work with the following conditions:&lt;/p&gt;
&lt;p&gt;THIS SOFTWARE IS PROVIDED ''AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE INSTITUTE OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
&lt;/p&gt;</description>
<packages>
<package name="SC70-5">
<wire x1="-1.1" y1="0.5" x2="1.1" y2="0.5" width="0.2032" layer="51"/>
<wire x1="1.1" y1="0.5" x2="1.1" y2="-0.5" width="0.2032" layer="21"/>
<wire x1="1.1" y1="-0.5" x2="-1.1" y2="-0.5" width="0.2032" layer="51"/>
<wire x1="-1.1" y1="-0.5" x2="-1.1" y2="0.5" width="0.2032" layer="21"/>
<smd name="1" x="-0.65" y="-0.85" dx="0.35" dy="1.15" layer="1"/>
<smd name="2" x="0" y="-0.85" dx="0.35" dy="1.15" layer="1"/>
<smd name="3" x="0.65" y="-0.85" dx="0.35" dy="1.15" layer="1"/>
<smd name="4" x="0.65" y="0.85" dx="0.35" dy="1.15" layer="1"/>
<smd name="5" x="-0.65" y="0.85" dx="0.35" dy="1.15" layer="1"/>
<text x="-1.2" y="1.477" size="0.8128" layer="25" ratio="18">&gt;NAME</text>
<text x="-1.2" y="-2.35" size="0.4064" layer="27" ratio="10">&gt;VALUE</text>
<rectangle x1="-0.8" y1="-1.1" x2="-0.5" y2="-0.6" layer="51"/>
<rectangle x1="-0.15" y1="-1.1" x2="0.15" y2="-0.6" layer="51"/>
<rectangle x1="0.5" y1="-1.1" x2="0.8" y2="-0.6" layer="51"/>
<rectangle x1="0.5" y1="0.6" x2="0.8" y2="1.1" layer="51"/>
<rectangle x1="-0.8" y1="0.6" x2="-0.5" y2="1.1" layer="51"/>
</package>
<package name="0603">
<description>0603 (1608 Metric)</description>
<wire x1="-1.473" y1="0.729" x2="1.473" y2="0.729" width="0.0508" layer="39"/>
<wire x1="1.473" y1="0.729" x2="1.473" y2="-0.729" width="0.0508" layer="39"/>
<wire x1="1.473" y1="-0.729" x2="-1.473" y2="-0.729" width="0.0508" layer="39"/>
<wire x1="-1.473" y1="-0.729" x2="-1.473" y2="0.729" width="0.0508" layer="39"/>
<wire x1="-0.356" y1="0.432" x2="0.356" y2="0.432" width="0.1016" layer="51"/>
<wire x1="-0.356" y1="-0.419" x2="0.356" y2="-0.419" width="0.1016" layer="51"/>
<wire x1="-1.6" y1="0.7" x2="1.6" y2="0.7" width="0.2032" layer="21"/>
<wire x1="1.6" y1="0.7" x2="1.6" y2="-0.7" width="0.2032" layer="21"/>
<wire x1="1.6" y1="-0.7" x2="-1.6" y2="-0.7" width="0.2032" layer="21"/>
<wire x1="-1.6" y1="-0.7" x2="-1.6" y2="0.7" width="0.2032" layer="21"/>
<smd name="1" x="-0.85" y="0" dx="1.1" dy="1" layer="1"/>
<smd name="2" x="0.85" y="0" dx="1.1" dy="1" layer="1"/>
<text x="1.778" y="-0.127" size="0.8128" layer="25" font="vector" ratio="18">&gt;NAME</text>
<text x="1.778" y="-0.762" size="0.4064" layer="27" font="vector" ratio="10">&gt;VALUE</text>
<rectangle x1="-0.8382" y1="-0.4699" x2="-0.3381" y2="0.4801" layer="51"/>
<rectangle x1="0.3302" y1="-0.4699" x2="0.8303" y2="0.4801" layer="51"/>
<rectangle x1="-0.1999" y1="-0.3" x2="0.1999" y2="0.3" layer="35"/>
</package>
<package name="0805">
<description>0805 (2012 Metric)</description>
<wire x1="-1.873" y1="0.883" x2="1.873" y2="0.883" width="0.0508" layer="39"/>
<wire x1="1.873" y1="-0.883" x2="-1.873" y2="-0.883" width="0.0508" layer="39"/>
<wire x1="-1.873" y1="-0.883" x2="-1.873" y2="0.883" width="0.0508" layer="39"/>
<wire x1="-0.381" y1="0.66" x2="0.381" y2="0.66" width="0.1016" layer="51"/>
<wire x1="-0.356" y1="-0.66" x2="0.381" y2="-0.66" width="0.1016" layer="51"/>
<wire x1="1.873" y1="0.883" x2="1.873" y2="-0.883" width="0.0508" layer="39"/>
<wire x1="1.8" y1="0.9" x2="1.8" y2="-0.9" width="0.2032" layer="21"/>
<wire x1="1.8" y1="-0.9" x2="-1.8" y2="-0.9" width="0.2032" layer="21"/>
<wire x1="-1.8" y1="-0.9" x2="-1.8" y2="0.9" width="0.2032" layer="21"/>
<wire x1="-1.8" y1="0.9" x2="1.8" y2="0.9" width="0.2032" layer="21"/>
<smd name="1" x="-0.95" y="0" dx="1.3" dy="1.5" layer="1"/>
<smd name="2" x="0.95" y="0" dx="1.3" dy="1.5" layer="1"/>
<text x="2.032" y="-0.127" size="0.8128" layer="25" ratio="18">&gt;NAME</text>
<text x="2.032" y="-0.762" size="0.4064" layer="27" ratio="10">&gt;VALUE</text>
<rectangle x1="-1.0922" y1="-0.7239" x2="-0.3421" y2="0.7262" layer="51"/>
<rectangle x1="0.3556" y1="-0.7239" x2="1.1057" y2="0.7262" layer="51"/>
<rectangle x1="-0.1001" y1="-0.4001" x2="0.1001" y2="0.4001" layer="35"/>
</package>
<package name="_0402">
<description>&lt;b&gt; 0402&lt;/b&gt;</description>
<wire x1="-0.245" y1="0.174" x2="0.245" y2="0.174" width="0.1016" layer="51"/>
<wire x1="0.245" y1="-0.174" x2="-0.245" y2="-0.174" width="0.1016" layer="51"/>
<wire x1="-1.0573" y1="0.5557" x2="1.0573" y2="0.5557" width="0.2032" layer="21"/>
<wire x1="1.0573" y1="0.5557" x2="1.0573" y2="-0.5556" width="0.2032" layer="21"/>
<wire x1="1.0573" y1="-0.5556" x2="-1.0573" y2="-0.5557" width="0.2032" layer="21"/>
<wire x1="-1.0573" y1="-0.5557" x2="-1.0573" y2="0.5557" width="0.2032" layer="21"/>
<smd name="1" x="-0.508" y="0" dx="0.6" dy="0.6" layer="1"/>
<smd name="2" x="0.508" y="0" dx="0.6" dy="0.6" layer="1"/>
<text x="-0.9525" y="0.7939" size="0.8128" layer="25" ratio="18">&gt;NAME</text>
<text x="-0.9525" y="-1.3336" size="0.4064" layer="27" ratio="10">&gt;VALUE</text>
<rectangle x1="-0.0794" y1="-0.2381" x2="0.0794" y2="0.2381" layer="35"/>
<rectangle x1="0.25" y1="-0.25" x2="0.5" y2="0.25" layer="51"/>
<rectangle x1="-0.5" y1="-0.25" x2="-0.25" y2="0.25" layer="51"/>
</package>
<package name="_0402MP">
<description>&lt;b&gt;0402 MicroPitch&lt;p&gt;</description>
<wire x1="-0.245" y1="0.174" x2="0.245" y2="0.174" width="0.1016" layer="51"/>
<wire x1="0.245" y1="-0.174" x2="-0.245" y2="-0.174" width="0.1016" layer="51"/>
<wire x1="0" y1="0.127" x2="0" y2="-0.127" width="0.2032" layer="21"/>
<smd name="1" x="-0.508" y="0" dx="0.5" dy="0.5" layer="1"/>
<smd name="2" x="0.508" y="0" dx="0.5" dy="0.5" layer="1"/>
<text x="-0.635" y="0.4763" size="0.6096" layer="25" ratio="18">&gt;NAME</text>
<text x="-0.635" y="-0.7938" size="0.4064" layer="27" ratio="10">&gt;VALUE</text>
<rectangle x1="-0.1" y1="-0.2" x2="0.1" y2="0.2" layer="35"/>
<rectangle x1="-0.5" y1="-0.25" x2="-0.254" y2="0.25" layer="51"/>
<rectangle x1="0.2588" y1="-0.25" x2="0.5" y2="0.25" layer="51"/>
</package>
<package name="_0603">
<description>&lt;b&gt;0603&lt;/b&gt;</description>
<wire x1="-0.432" y1="-0.306" x2="0.432" y2="-0.306" width="0.1016" layer="51"/>
<wire x1="0.432" y1="0.306" x2="-0.432" y2="0.306" width="0.1016" layer="51"/>
<wire x1="-1.4605" y1="0.635" x2="1.4605" y2="0.635" width="0.2032" layer="21"/>
<wire x1="1.4605" y1="0.635" x2="1.4605" y2="-0.635" width="0.2032" layer="21"/>
<wire x1="1.4605" y1="-0.635" x2="-1.4605" y2="-0.635" width="0.2032" layer="21"/>
<wire x1="-1.4605" y1="-0.635" x2="-1.4605" y2="0.635" width="0.2032" layer="21"/>
<smd name="1" x="-0.762" y="0" dx="0.9" dy="0.8" layer="1"/>
<smd name="2" x="0.762" y="0" dx="0.9" dy="0.8" layer="1"/>
<text x="-1.27" y="0.9525" size="0.8128" layer="25" ratio="18">&gt;NAME</text>
<text x="-1.27" y="-1.4923" size="0.4064" layer="27" ratio="10">&gt;VALUE</text>
<rectangle x1="0.4318" y1="-0.4" x2="0.8382" y2="0.4" layer="51"/>
<rectangle x1="-0.8382" y1="-0.4" x2="-0.4318" y2="0.4" layer="51"/>
<rectangle x1="-0.1999" y1="-0.4001" x2="0.1999" y2="0.4001" layer="35"/>
</package>
<package name="_0603MP">
<description>&lt;b&gt;0603 MicroPitch&lt;/b&gt;</description>
<wire x1="-0.432" y1="-0.306" x2="0.432" y2="-0.306" width="0.1016" layer="51"/>
<wire x1="0.432" y1="0.306" x2="-0.432" y2="0.306" width="0.1016" layer="51"/>
<wire x1="0" y1="0.254" x2="0" y2="-0.254" width="0.2032" layer="21"/>
<smd name="1" x="-0.762" y="0" dx="0.8" dy="0.8" layer="1"/>
<smd name="2" x="0.762" y="0" dx="0.8" dy="0.8" layer="1"/>
<text x="-0.9525" y="0.635" size="0.8128" layer="25" ratio="18">&gt;NAME</text>
<text x="-0.9525" y="-0.9525" size="0.4064" layer="27" ratio="10">&gt;VALUE</text>
<rectangle x1="0.4318" y1="-0.4" x2="0.8" y2="0.4" layer="51"/>
<rectangle x1="-0.8" y1="-0.4" x2="-0.4318" y2="0.4" layer="51"/>
<rectangle x1="-0.1999" y1="-0.25" x2="0.1999" y2="0.25" layer="35"/>
</package>
<package name="_0805">
<description>&lt;b&gt;0805&lt;/b&gt;</description>
<wire x1="-0.41" y1="0.585" x2="0.41" y2="0.585" width="0.1016" layer="51"/>
<wire x1="-0.41" y1="-0.585" x2="0.41" y2="-0.585" width="0.1016" layer="51"/>
<wire x1="-1.905" y1="0.889" x2="1.905" y2="0.889" width="0.2032" layer="21"/>
<wire x1="1.905" y1="0.889" x2="1.905" y2="-0.889" width="0.2032" layer="21"/>
<wire x1="1.905" y1="-0.889" x2="-1.905" y2="-0.889" width="0.2032" layer="21"/>
<wire x1="-1.905" y1="-0.889" x2="-1.905" y2="0.889" width="0.2032" layer="21"/>
<smd name="1" x="-1.016" y="0" dx="1.2" dy="1.3" layer="1"/>
<smd name="2" x="1.016" y="0" dx="1.2" dy="1.3" layer="1"/>
<text x="-1.5875" y="1.27" size="0.8128" layer="25" ratio="18">&gt;NAME</text>
<text x="-1.5874" y="-1.651" size="0.4064" layer="27" ratio="10">&gt;VALUE</text>
<rectangle x1="0.4064" y1="-0.65" x2="1.0564" y2="0.65" layer="51"/>
<rectangle x1="-1.0668" y1="-0.65" x2="-0.4168" y2="0.65" layer="51"/>
<rectangle x1="-0.1999" y1="-0.5001" x2="0.1999" y2="0.5001" layer="35"/>
</package>
<package name="_0805MP">
<description>&lt;b&gt;0805 MicroPitch&lt;/b&gt;</description>
<wire x1="-0.51" y1="0.535" x2="0.51" y2="0.535" width="0.1016" layer="51"/>
<wire x1="-0.51" y1="-0.535" x2="0.51" y2="-0.535" width="0.1016" layer="51"/>
<wire x1="0" y1="0.508" x2="0" y2="-0.508" width="0.2032" layer="21"/>
<smd name="1" x="-1.016" y="0" dx="1.2" dy="1.3" layer="1"/>
<smd name="2" x="1.016" y="0" dx="1.2" dy="1.3" layer="1"/>
<text x="-1.5875" y="0.9525" size="0.8128" layer="25" ratio="18">&gt;NAME</text>
<text x="-1.5875" y="-1.27" size="0.4064" layer="27" ratio="10">&gt;VALUE</text>
<rectangle x1="0.4064" y1="-0.65" x2="1" y2="0.65" layer="51"/>
<rectangle x1="-1" y1="-0.65" x2="-0.4168" y2="0.65" layer="51"/>
<rectangle x1="-0.1999" y1="-0.5001" x2="0.1999" y2="0.5001" layer="35"/>
</package>
<package name="1206">
<description>1206 (3216 Metric)</description>
<wire x1="-2.473" y1="0.983" x2="2.473" y2="0.983" width="0.0508" layer="39"/>
<wire x1="2.473" y1="-0.983" x2="-2.473" y2="-0.983" width="0.0508" layer="39"/>
<wire x1="-2.473" y1="-0.983" x2="-2.473" y2="0.983" width="0.0508" layer="39"/>
<wire x1="2.473" y1="0.983" x2="2.473" y2="-0.983" width="0.0508" layer="39"/>
<wire x1="-0.965" y1="0.787" x2="0.965" y2="0.787" width="0.1016" layer="51"/>
<wire x1="-0.965" y1="-0.787" x2="0.965" y2="-0.787" width="0.1016" layer="51"/>
<wire x1="-2.4" y1="1" x2="2.4" y2="1" width="0.2032" layer="21"/>
<wire x1="2.4" y1="1" x2="2.4" y2="-1" width="0.2032" layer="21"/>
<wire x1="2.4" y1="-1" x2="-2.4" y2="-1" width="0.2032" layer="21"/>
<wire x1="-2.4" y1="-1" x2="-2.4" y2="1" width="0.2032" layer="21"/>
<smd name="1" x="-1.4" y="0" dx="1.6" dy="1.8" layer="1"/>
<smd name="2" x="1.4" y="0" dx="1.6" dy="1.8" layer="1"/>
<text x="2.54" y="-0.127" size="0.8128" layer="25" ratio="18">&gt;NAME</text>
<text x="2.54" y="-0.635" size="0.4064" layer="27" ratio="10">&gt;VALUE</text>
<rectangle x1="-1.7018" y1="-0.8509" x2="-0.9517" y2="0.8491" layer="51"/>
<rectangle x1="0.9517" y1="-0.8491" x2="1.7018" y2="0.8509" layer="51"/>
<rectangle x1="-0.1999" y1="-0.4001" x2="0.1999" y2="0.4001" layer="35"/>
</package>
<package name="0402">
<description>&lt;b&gt;CAPACITOR&lt;/b&gt;&lt;p&gt;
chip</description>
<wire x1="-0.245" y1="0.224" x2="0.245" y2="0.224" width="0.2032" layer="51"/>
<wire x1="0.245" y1="-0.224" x2="-0.245" y2="-0.224" width="0.2032" layer="51"/>
<wire x1="-1.346" y1="0.483" x2="1.346" y2="0.483" width="0.0508" layer="39"/>
<wire x1="1.346" y1="0.483" x2="1.346" y2="-0.483" width="0.0508" layer="39"/>
<wire x1="1.346" y1="-0.483" x2="-1.346" y2="-0.483" width="0.0508" layer="39"/>
<wire x1="-1.346" y1="-0.483" x2="-1.346" y2="0.483" width="0.0508" layer="39"/>
<wire x1="-1.27" y1="-0.635" x2="-1.27" y2="0.635" width="0.2032" layer="21"/>
<wire x1="-1.27" y1="0.635" x2="1.27" y2="0.635" width="0.2032" layer="21"/>
<wire x1="1.27" y1="0.635" x2="1.27" y2="-0.635" width="0.2032" layer="21"/>
<wire x1="1.27" y1="-0.635" x2="-1.27" y2="-0.635" width="0.2032" layer="21"/>
<smd name="1" x="-0.65" y="0" dx="0.7" dy="0.9" layer="1"/>
<smd name="2" x="0.65" y="0" dx="0.7" dy="0.9" layer="1"/>
<text x="1.397" y="-0.1905" size="0.8128" layer="25" ratio="18">&gt;NAME</text>
<text x="1.397" y="-0.635" size="0.4064" layer="27" ratio="10">&gt;VALUE</text>
<rectangle x1="-0.554" y1="-0.3048" x2="-0.254" y2="0.2951" layer="51"/>
<rectangle x1="0.2588" y1="-0.3048" x2="0.5588" y2="0.2951" layer="51"/>
<rectangle x1="-0.1999" y1="-0.3" x2="0.1999" y2="0.3" layer="35"/>
</package>
<package name="0603-MINI">
<description>0603-Mini
&lt;p&gt;Mini footprint for dense boards&lt;/p&gt;</description>
<wire x1="-1.346" y1="0.583" x2="1.346" y2="0.583" width="0.0508" layer="39"/>
<wire x1="1.346" y1="0.583" x2="1.346" y2="-0.583" width="0.0508" layer="39"/>
<wire x1="1.346" y1="-0.583" x2="-1.346" y2="-0.583" width="0.0508" layer="39"/>
<wire x1="-1.346" y1="-0.583" x2="-1.346" y2="0.583" width="0.0508" layer="39"/>
<wire x1="-1.37" y1="-0.635" x2="-1.37" y2="0.635" width="0.2032" layer="21"/>
<wire x1="-1.37" y1="0.635" x2="1.37" y2="0.635" width="0.2032" layer="21"/>
<wire x1="1.37" y1="0.635" x2="1.37" y2="-0.635" width="0.2032" layer="21"/>
<wire x1="1.37" y1="-0.635" x2="-1.37" y2="-0.635" width="0.2032" layer="21"/>
<wire x1="-0.356" y1="0.432" x2="0.356" y2="0.432" width="0.1016" layer="51"/>
<wire x1="-0.356" y1="-0.419" x2="0.356" y2="-0.419" width="0.1016" layer="51"/>
<smd name="1" x="-0.75" y="0" dx="0.9" dy="0.9" layer="1"/>
<smd name="2" x="0.75" y="0" dx="0.9" dy="0.9" layer="1"/>
<text x="1.524" y="-0.0635" size="0.8128" layer="25" ratio="18">&gt;NAME</text>
<text x="1.524" y="-0.635" size="0.4064" layer="27" ratio="10">&gt;VALUE</text>
<rectangle x1="-0.8382" y1="-0.4699" x2="-0.3381" y2="0.4801" layer="51"/>
<rectangle x1="0.3302" y1="-0.4699" x2="0.8303" y2="0.4801" layer="51"/>
</package>
<package name="2012">
<wire x1="-1.662" y1="1.245" x2="1.662" y2="1.245" width="0.2032" layer="51"/>
<wire x1="-1.637" y1="-1.245" x2="1.687" y2="-1.245" width="0.2032" layer="51"/>
<wire x1="-3.473" y1="1.483" x2="3.473" y2="1.483" width="0.0508" layer="39"/>
<wire x1="3.473" y1="1.483" x2="3.473" y2="-1.483" width="0.0508" layer="39"/>
<wire x1="3.473" y1="-1.483" x2="-3.473" y2="-1.483" width="0.0508" layer="39"/>
<wire x1="-3.473" y1="-1.483" x2="-3.473" y2="1.483" width="0.0508" layer="39"/>
<wire x1="-3.302" y1="1.524" x2="3.302" y2="1.524" width="0.2032" layer="21"/>
<wire x1="3.302" y1="1.524" x2="3.302" y2="-1.524" width="0.2032" layer="21"/>
<wire x1="3.302" y1="-1.524" x2="-3.302" y2="-1.524" width="0.2032" layer="21"/>
<wire x1="-3.302" y1="-1.524" x2="-3.302" y2="1.524" width="0.2032" layer="21"/>
<smd name="1" x="-2.2" y="0" dx="1.8" dy="2.7" layer="1"/>
<smd name="2" x="2.2" y="0" dx="1.8" dy="2.7" layer="1"/>
<text x="-2.54" y="1.8415" size="0.8128" layer="25" ratio="18">&gt;NAME</text>
<text x="-2.667" y="-2.159" size="0.4064" layer="27" ratio="10">&gt;VALUE</text>
<rectangle x1="-2.4892" y1="-1.3208" x2="-1.6393" y2="1.3292" layer="51"/>
<rectangle x1="1.651" y1="-1.3208" x2="2.5009" y2="1.3292" layer="51"/>
</package>
<package name="0805_NOTHERMALS">
<wire x1="-1.873" y1="0.883" x2="1.873" y2="0.883" width="0.0508" layer="39"/>
<wire x1="1.873" y1="-0.883" x2="-1.873" y2="-0.883" width="0.0508" layer="39"/>
<wire x1="-1.873" y1="-0.883" x2="-1.873" y2="0.883" width="0.0508" layer="39"/>
<wire x1="-0.381" y1="0.66" x2="0.381" y2="0.66" width="0.1016" layer="51"/>
<wire x1="-0.356" y1="-0.66" x2="0.381" y2="-0.66" width="0.1016" layer="51"/>
<wire x1="1.873" y1="0.883" x2="1.873" y2="-0.883" width="0.0508" layer="39"/>
<wire x1="1.8" y1="0.9" x2="1.8" y2="-0.9" width="0.2032" layer="21"/>
<wire x1="1.8" y1="-0.9" x2="-1.8" y2="-0.9" width="0.2032" layer="21"/>
<wire x1="-1.8" y1="-0.9" x2="-1.8" y2="0.9" width="0.2032" layer="21"/>
<wire x1="-1.8" y1="0.9" x2="1.8" y2="0.9" width="0.2032" layer="21"/>
<smd name="1" x="-0.95" y="0" dx="1.3" dy="1.5" layer="1" thermals="no"/>
<smd name="2" x="0.95" y="0" dx="1.3" dy="1.5" layer="1" thermals="no"/>
<text x="2.032" y="-0.127" size="0.8128" layer="25" ratio="18">&gt;NAME</text>
<text x="2.032" y="-0.762" size="0.4064" layer="27" ratio="10">&gt;VALUE</text>
<rectangle x1="-1.0922" y1="-0.7239" x2="-0.3421" y2="0.7262" layer="51"/>
<rectangle x1="0.3556" y1="-0.7239" x2="1.1057" y2="0.7262" layer="51"/>
</package>
<package name="2512">
<description>&lt;b&gt;RESISTOR 2512 (Metric 6432)&lt;/b&gt;</description>
<wire x1="-2.362" y1="1.473" x2="2.387" y2="1.473" width="0.2032" layer="51"/>
<wire x1="-2.362" y1="-1.473" x2="2.387" y2="-1.473" width="0.2032" layer="51"/>
<wire x1="-3.973" y1="1.983" x2="3.973" y2="1.983" width="0.0508" layer="39"/>
<wire x1="3.973" y1="1.983" x2="3.973" y2="-1.983" width="0.0508" layer="39"/>
<wire x1="3.973" y1="-1.983" x2="-3.973" y2="-1.983" width="0.0508" layer="39"/>
<wire x1="-3.973" y1="-1.983" x2="-3.973" y2="1.983" width="0.0508" layer="39"/>
<smd name="1" x="-2.8" y="0" dx="1.8" dy="3.2" layer="1"/>
<smd name="2" x="2.8" y="0" dx="1.8" dy="3.2" layer="1"/>
<text x="-3.683" y="1.905" size="0.8128" layer="25" ratio="18">&gt;NAME</text>
<text x="-3.556" y="-2.286" size="0.4064" layer="27" ratio="10">&gt;VALUE</text>
<rectangle x1="-3.2004" y1="-1.5494" x2="-2.3505" y2="1.5507" layer="51"/>
<rectangle x1="2.3622" y1="-1.5494" x2="3.2121" y2="1.5507" layer="51"/>
<rectangle x1="-0.5001" y1="-1" x2="0.5001" y2="1" layer="35"/>
</package>
<package name="TRIMPOT_BOURNS_3303W">
<description>&lt;p&gt;Bourns 3303W 3MM SMT Trimpot&lt;/p&gt;</description>
<wire x1="-1.55" y1="1.55" x2="1.55" y2="1.55" width="0.2032" layer="51"/>
<wire x1="1.55" y1="1.55" x2="1.55" y2="-1.55" width="0.127" layer="51"/>
<wire x1="1.55" y1="-1.55" x2="-1.55" y2="-1.55" width="0.127" layer="51"/>
<wire x1="-1.55" y1="-1.55" x2="-1.55" y2="1.55" width="0.127" layer="51"/>
<wire x1="-0.35" y1="-0.15" x2="-1.15" y2="-0.15" width="0.2032" layer="51"/>
<wire x1="-1.15" y1="-0.15" x2="-1.15" y2="0.2" width="0.2032" layer="51"/>
<wire x1="-1.15" y1="0.2" x2="-0.4" y2="0.2" width="0.2032" layer="51"/>
<wire x1="-0.4" y1="0.2" x2="-0.4" y2="-0.1" width="0.2032" layer="51"/>
<wire x1="-0.15" y1="0.4" x2="-0.15" y2="1.15" width="0.2032" layer="51"/>
<wire x1="-0.15" y1="1.15" x2="0.2" y2="1.15" width="0.2032" layer="51"/>
<wire x1="0.2" y1="1.15" x2="0.2" y2="0.4" width="0.2032" layer="51"/>
<wire x1="0.2" y1="0.4" x2="-0.15" y2="0.4" width="0.2032" layer="51"/>
<wire x1="0.4" y1="0.2" x2="1.15" y2="0.2" width="0.2032" layer="51"/>
<wire x1="1.15" y1="0.2" x2="1.15" y2="-0.15" width="0.2032" layer="51"/>
<wire x1="1.15" y1="-0.15" x2="0.4" y2="-0.15" width="0.2032" layer="51"/>
<wire x1="0.4" y1="-0.15" x2="0.4" y2="0.2" width="0.2032" layer="51"/>
<wire x1="-0.15" y1="-0.35" x2="-0.15" y2="-1.15" width="0.2032" layer="51"/>
<wire x1="-0.15" y1="-1.15" x2="0.2" y2="-1.15" width="0.2032" layer="51"/>
<wire x1="0.2" y1="-1.15" x2="0.2" y2="-0.35" width="0.2032" layer="51"/>
<wire x1="-1.55" y1="-0.85" x2="-1.55" y2="1.55" width="0.2032" layer="21"/>
<wire x1="-1.55" y1="1.55" x2="-0.95" y2="1.55" width="0.2032" layer="21"/>
<wire x1="0.9" y1="1.55" x2="1.55" y2="1.55" width="0.2032" layer="21"/>
<wire x1="1.55" y1="1.55" x2="1.55" y2="-0.85" width="0.2032" layer="21"/>
<wire x1="-0.3" y1="-1.55" x2="0.25" y2="-1.55" width="0.2032" layer="21"/>
<circle x="0" y="0" radius="1.2419" width="0.2032" layer="51"/>
<circle x="0" y="0" radius="0.3905" width="0.2032" layer="51"/>
<smd name="2" x="0" y="1.65" dx="1.6" dy="1.5" layer="1"/>
<smd name="1" x="-1" y="-1.6" dx="1.2" dy="1.2" layer="1" rot="R90"/>
<smd name="3" x="1" y="-1.6" dx="1.2" dy="1.2" layer="1" rot="R90"/>
<text x="-2.54" y="-2.54" size="0.8128" layer="25" ratio="18" rot="R90">&gt;NAME</text>
<text x="2.413" y="-2.54" size="0.4064" layer="25" ratio="10" rot="R90">&gt;VALUE</text>
</package>
<package name="TRIMPOT_BOURNS_TC33X-2">
<description>&lt;p&gt;Source: http://www.bourns.com/data/global/PDFs/TC33.PDF&lt;/p&gt;</description>
<text x="1.65" y="-0.21" size="0.8128" layer="25" ratio="18">&gt;NAME</text>
<text x="1.65" y="-0.863" size="0.4064" layer="25" ratio="10">&gt;VALUE</text>
<wire x1="0.3" y1="1.52" x2="0.3" y2="1.31" width="0.05" layer="51"/>
<wire x1="0.3" y1="1.31" x2="-0.33" y2="1.31" width="0.05" layer="51"/>
<wire x1="-0.33" y1="1.31" x2="-0.33" y2="1.51" width="0.05" layer="51"/>
<wire x1="-0.33" y1="1.51" x2="-1.15" y2="1.51" width="0.05" layer="51"/>
<wire x1="-1.15" y1="1.51" x2="-1.29" y2="1.37" width="0.05" layer="51" curve="-90"/>
<wire x1="-1.29" y1="1.37" x2="-1.29" y2="-1.48" width="0.05" layer="51"/>
<wire x1="-1.29" y1="-1.48" x2="-1.14" y2="-1.63" width="0.05" layer="51" curve="-90"/>
<wire x1="-1.14" y1="-1.63" x2="-1.14" y2="-1.75" width="0.05" layer="51"/>
<wire x1="-1.14" y1="-1.75" x2="-0.34" y2="-1.75" width="0.05" layer="51"/>
<wire x1="-0.34" y1="-1.75" x2="-0.34" y2="-1.62" width="0.05" layer="51"/>
<wire x1="-0.34" y1="-1.62" x2="-0.31" y2="-1.59" width="0.05" layer="51"/>
<wire x1="-0.31" y1="-1.59" x2="0.29" y2="-1.59" width="0.05" layer="51"/>
<wire x1="0.29" y1="-1.59" x2="0.32" y2="-1.62" width="0.05" layer="51"/>
<wire x1="0.32" y1="-1.62" x2="0.32" y2="-1.75" width="0.05" layer="51"/>
<wire x1="0.32" y1="-1.75" x2="1.13" y2="-1.75" width="0.05" layer="51"/>
<wire x1="1.13" y1="-1.75" x2="1.13" y2="-1.62" width="0.05" layer="51"/>
<wire x1="1.13" y1="-1.62" x2="1.26" y2="-1.49" width="0.05" layer="51" curve="-90"/>
<wire x1="1.26" y1="-1.49" x2="1.26" y2="1.39" width="0.05" layer="51"/>
<wire x1="1.26" y1="1.39" x2="1.25" y2="1.39" width="0.05" layer="51"/>
<wire x1="1.25" y1="1.39" x2="1.12" y2="1.52" width="0.05" layer="51" curve="-90"/>
<wire x1="1.12" y1="1.52" x2="0.62" y2="1.52" width="0.05" layer="51"/>
<wire x1="0.62" y1="1.52" x2="0.3" y2="1.52" width="0.05" layer="51"/>
<wire x1="-1.51" y1="0" x2="-1.51" y2="0.05" width="0.05" layer="51" style="shortdash"/>
<wire x1="-1.51" y1="0.05" x2="0.01" y2="1.57" width="0.05" layer="51" style="shortdash" curve="-90"/>
<wire x1="0.01" y1="1.57" x2="1.49" y2="0" width="0.05" layer="51" style="shortdash" curve="-90"/>
<wire x1="1.49" y1="0" x2="1.49" y2="-0.06" width="0.05" layer="51" style="shortdash"/>
<wire x1="1.49" y1="-0.06" x2="0" y2="-1.55" width="0.05" layer="51" style="shortdash" curve="-90"/>
<wire x1="0" y1="-1.55" x2="0.01" y2="-1.55" width="0.05" layer="51" style="shortdash"/>
<wire x1="0.01" y1="-1.55" x2="-1.51" y2="0" width="0.05" layer="51" style="shortdash" curve="-90"/>
<wire x1="-0.81" y1="1.03" x2="-0.63" y2="-1.15" width="0.05" layer="51" curve="105"/>
<wire x1="-0.63" y1="-1.15" x2="-0.63" y2="-1.28" width="0.05" layer="51"/>
<wire x1="-0.63" y1="-1.28" x2="-0.63" y2="-1.36" width="0.05" layer="51"/>
<wire x1="-0.63" y1="-1.36" x2="0.28" y2="-1.36" width="0.05" layer="51"/>
<wire x1="0.28" y1="-1.36" x2="0.63" y2="-1.36" width="0.05" layer="51"/>
<wire x1="0.63" y1="-1.36" x2="0.63" y2="-1.15" width="0.05" layer="51"/>
<wire x1="0.63" y1="-1.15" x2="0.83" y2="1.03" width="0.05" layer="51" curve="105"/>
<wire x1="-0.81" y1="1.03" x2="-0.62" y2="1.03" width="0.05" layer="51"/>
<wire x1="-0.46" y1="1.03" x2="-0.32" y2="1.03" width="0.05" layer="51"/>
<wire x1="-0.32" y1="1.03" x2="0.01" y2="1.24" width="0.05" layer="51" curve="-60"/>
<wire x1="0.01" y1="1.24" x2="0.34" y2="1.03" width="0.05" layer="51" curve="-60"/>
<wire x1="0.34" y1="1.03" x2="0.45" y2="1.03" width="0.05" layer="51"/>
<wire x1="0.61" y1="1.03" x2="0.83" y2="1.03" width="0.05" layer="51"/>
<wire x1="-0.6" y1="1.04" x2="-0.32" y2="1.17" width="0.05" layer="51"/>
<wire x1="-0.32" y1="1.17" x2="-0.23" y2="1.17" width="0.05" layer="51"/>
<wire x1="-0.23" y1="1.17" x2="-0.46" y2="1.03" width="0.05" layer="51"/>
<wire x1="-0.46" y1="1.03" x2="-0.62" y2="1.03" width="0.05" layer="51"/>
<wire x1="-0.62" y1="1.03" x2="-0.58" y2="1.05" width="0.05" layer="51"/>
<wire x1="0.26" y1="1.17" x2="0.32" y2="1.17" width="0.05" layer="51"/>
<wire x1="0.32" y1="1.17" x2="0.61" y2="1.03" width="0.05" layer="51"/>
<wire x1="0.61" y1="1.03" x2="0.45" y2="1.03" width="0.05" layer="51"/>
<wire x1="0.45" y1="1.03" x2="0.26" y2="1.17" width="0.05" layer="51"/>
<wire x1="-0.52" y1="0.22" x2="-0.84" y2="0.22" width="0.05" layer="51"/>
<wire x1="-0.84" y1="0.22" x2="-0.91" y2="0.22" width="0.05" layer="51"/>
<wire x1="-0.91" y1="0.22" x2="-0.91" y2="-0.24" width="0.05" layer="51"/>
<wire x1="-0.91" y1="-0.24" x2="-0.51" y2="-0.24" width="0.05" layer="51"/>
<wire x1="-0.51" y1="-0.24" x2="-0.5" y2="-0.25" width="0.05" layer="51"/>
<wire x1="-0.5" y1="-0.25" x2="0.51" y2="-0.25" width="0.05" layer="51" curve="130"/>
<wire x1="0.51" y1="-0.25" x2="0.52" y2="-0.24" width="0.05" layer="51"/>
<wire x1="0.52" y1="-0.24" x2="0.9" y2="-0.24" width="0.05" layer="51"/>
<wire x1="0.9" y1="-0.24" x2="0.9" y2="0.22" width="0.05" layer="51"/>
<wire x1="0.9" y1="0.22" x2="0.82" y2="0.22" width="0.05" layer="51"/>
<wire x1="0.82" y1="0.22" x2="0.53" y2="0.22" width="0.05" layer="51"/>
<wire x1="0.53" y1="0.22" x2="0.53" y2="0.23" width="0.05" layer="51"/>
<wire x1="0.53" y1="0.23" x2="-0.52" y2="0.23" width="0.05" layer="51" curve="130"/>
<wire x1="-0.52" y1="0.23" x2="-0.52" y2="0.22" width="0.05" layer="51"/>
<wire x1="-0.22" y1="0.53" x2="-0.22" y2="0.93" width="0.05" layer="51"/>
<wire x1="-0.22" y1="0.93" x2="0.21" y2="0.93" width="0.05" layer="51"/>
<wire x1="0.21" y1="0.93" x2="0.21" y2="0.54" width="0.05" layer="51"/>
<wire x1="-0.22" y1="-0.52" x2="-0.22" y2="-0.94" width="0.05" layer="51"/>
<wire x1="-0.22" y1="-0.94" x2="0.21" y2="-0.94" width="0.05" layer="51"/>
<wire x1="0.21" y1="-0.94" x2="0.21" y2="-0.53" width="0.05" layer="51"/>
<wire x1="-0.84" y1="0.22" x2="-0.84" y2="-0.23" width="0.05" layer="51"/>
<wire x1="0.82" y1="0.22" x2="0.82" y2="-0.23" width="0.05" layer="51"/>
<circle x="0" y="0" radius="0.202484375" width="0.05" layer="51"/>
<circle x="0" y="0" radius="0.31064375" width="0.05" layer="51"/>
<circle x="0" y="0" radius="0.399246875" width="0.05" layer="51"/>
<circle x="0" y="0" radius="0.738240625" width="0.05" layer="51"/>
<wire x1="-0.64" y1="1.52" x2="-0.64" y2="1.58" width="0.05" layer="51"/>
<wire x1="-0.64" y1="1.58" x2="-0.33" y2="1.58" width="0.05" layer="51"/>
<wire x1="-0.33" y1="1.58" x2="-0.33" y2="1.52" width="0.05" layer="51"/>
<wire x1="0.3" y1="1.52" x2="0.3" y2="1.58" width="0.05" layer="51"/>
<wire x1="0.3" y1="1.58" x2="0.62" y2="1.58" width="0.05" layer="51"/>
<wire x1="0.62" y1="1.58" x2="0.62" y2="1.52" width="0.05" layer="51"/>
<wire x1="-1.14" y1="-0.58" x2="-1.14" y2="-0.9" width="0.05" layer="51"/>
<wire x1="-1.14" y1="-0.9" x2="-0.93" y2="-0.9" width="0.05" layer="51"/>
<wire x1="1.12" y1="-0.63" x2="1.12" y2="-0.9" width="0.05" layer="51"/>
<wire x1="1.12" y1="-0.9" x2="0.94" y2="-0.9" width="0.05" layer="51"/>
<wire x1="-0.63" y1="-1.28" x2="-0.7" y2="-1.28" width="0.05" layer="51"/>
<wire x1="-0.7" y1="-1.28" x2="-0.75" y2="-1.33" width="0.05" layer="51"/>
<wire x1="-0.75" y1="-1.33" x2="-0.91" y2="-1.33" width="0.05" layer="51"/>
<wire x1="-0.91" y1="-1.33" x2="-1.07" y2="-1.19" width="0.05" layer="51" curve="-30"/>
<wire x1="-1.07" y1="-1.19" x2="-1.14" y2="-1.19" width="0.05" layer="51"/>
<wire x1="-1.14" y1="-1.19" x2="-1.14" y2="-1.49" width="0.05" layer="51"/>
<wire x1="-1.14" y1="-1.49" x2="-1.05" y2="-1.58" width="0.05" layer="51"/>
<wire x1="-1.05" y1="-1.58" x2="-0.37" y2="-1.58" width="0.05" layer="51"/>
<wire x1="-0.37" y1="-1.58" x2="-0.3" y2="-1.51" width="0.05" layer="51"/>
<wire x1="-0.3" y1="-1.51" x2="-0.3" y2="-1.37" width="0.05" layer="51"/>
<wire x1="0.64" y1="-1.29" x2="0.68" y2="-1.29" width="0.05" layer="51"/>
<wire x1="0.68" y1="-1.29" x2="0.73" y2="-1.33" width="0.05" layer="51"/>
<wire x1="0.73" y1="-1.33" x2="0.89" y2="-1.33" width="0.05" layer="51"/>
<wire x1="0.89" y1="-1.33" x2="1.04" y2="-1.19" width="0.05" layer="51" curve="30"/>
<wire x1="1.04" y1="-1.19" x2="1.12" y2="-1.19" width="0.05" layer="51"/>
<wire x1="1.12" y1="-1.19" x2="1.12" y2="-1.5" width="0.05" layer="51"/>
<wire x1="1.12" y1="-1.5" x2="1.03" y2="-1.58" width="0.05" layer="51"/>
<wire x1="1.03" y1="-1.58" x2="0.35" y2="-1.58" width="0.05" layer="51"/>
<wire x1="0.35" y1="-1.58" x2="0.28" y2="-1.51" width="0.05" layer="51"/>
<wire x1="0.28" y1="-1.51" x2="0.28" y2="-1.36" width="0.05" layer="51"/>
<wire x1="-0.76" y1="-1.06" x2="-0.94" y2="-1.06" width="0.05" layer="51"/>
<wire x1="-0.94" y1="-1.06" x2="-0.94" y2="-1.3" width="0.05" layer="51"/>
<wire x1="-0.64" y1="-1.27" x2="-0.85" y2="-1.27" width="0.05" layer="51"/>
<wire x1="-0.85" y1="-1.27" x2="-0.69" y2="-1.12" width="0.05" layer="51"/>
<wire x1="0.64" y1="-1.28" x2="0.83" y2="-1.28" width="0.05" layer="51"/>
<wire x1="0.83" y1="-1.28" x2="0.68" y2="-1.13" width="0.05" layer="51"/>
<wire x1="0.77" y1="-1.05" x2="0.91" y2="-1.05" width="0.05" layer="51"/>
<wire x1="0.91" y1="-1.05" x2="0.91" y2="-1.31" width="0.05" layer="51"/>
<wire x1="-1.15" y1="-1.61" x2="-0.73" y2="-1.61" width="0.05" layer="51"/>
<wire x1="-0.73" y1="-1.61" x2="-0.73" y2="-1.74" width="0.05" layer="51"/>
<wire x1="-1.02" y1="-1.62" x2="-1.02" y2="-1.73" width="0.05" layer="51"/>
<wire x1="-1.01" y1="-1.68" x2="-0.75" y2="-1.68" width="0.05" layer="51"/>
<wire x1="-0.52" y1="-1.59" x2="-0.52" y2="-1.73" width="0.05" layer="51"/>
<wire x1="-0.46" y1="-1.6" x2="-0.46" y2="-1.73" width="0.05" layer="51"/>
<wire x1="-0.51" y1="-1.62" x2="-0.35" y2="-1.62" width="0.05" layer="51"/>
<wire x1="0.33" y1="-1.62" x2="0.49" y2="-1.62" width="0.05" layer="51"/>
<wire x1="0.5" y1="-1.6" x2="0.5" y2="-1.74" width="0.05" layer="51"/>
<wire x1="0.43" y1="-1.59" x2="0.43" y2="-1.74" width="0.05" layer="51"/>
<wire x1="1.13" y1="-1.61" x2="1" y2="-1.61" width="0.05" layer="51"/>
<wire x1="1" y1="-1.61" x2="0.71" y2="-1.61" width="0.05" layer="51"/>
<wire x1="0.71" y1="-1.59" x2="0.71" y2="-1.67" width="0.05" layer="51"/>
<wire x1="0.71" y1="-1.67" x2="0.71" y2="-1.73" width="0.05" layer="51"/>
<wire x1="1" y1="-1.61" x2="1" y2="-1.67" width="0.05" layer="51"/>
<wire x1="1" y1="-1.67" x2="1" y2="-1.74" width="0.05" layer="51"/>
<wire x1="1" y1="-1.67" x2="0.71" y2="-1.67" width="0.05" layer="51"/>
<smd name="2" x="0" y="1.45" dx="1.6" dy="1.5" layer="1"/>
<smd name="1" x="-1" y="-1.8" dx="1.2" dy="1.2" layer="1"/>
<smd name="3" x="1" y="-1.8" dx="1.2" dy="1.2" layer="1"/>
<wire x1="-0.9" y1="1.55" x2="-1.17" y2="1.55" width="0.05" layer="21"/>
<wire x1="-1.17" y1="1.55" x2="-1.33" y2="1.39" width="0.05" layer="21" curve="-90"/>
<wire x1="-1.33" y1="1.39" x2="-1.34" y2="-1.1" width="0.05" layer="21"/>
<wire x1="0.9" y1="1.56" x2="1.15" y2="1.56" width="0.05" layer="21"/>
<wire x1="1.15" y1="1.56" x2="1.3" y2="1.41" width="0.05" layer="21" curve="90"/>
<wire x1="1.3" y1="1.41" x2="1.31" y2="-1.09" width="0.05" layer="21"/>
</package>
</packages>
<symbols>
<symbol name="MAX4466">
<pin name="IN+" x="-12.7" y="2.54" length="short"/>
<pin name="IN-" x="-12.7" y="-2.54" length="short"/>
<pin name="GND" x="-12.7" y="-7.62" length="short"/>
<pin name="VCC" x="-12.7" y="7.62" length="short"/>
<pin name="OUT" x="12.7" y="0" length="short" rot="R180"/>
<wire x1="-10.16" y1="10.16" x2="10.16" y2="10.16" width="0.254" layer="94" style="shortdash"/>
<wire x1="10.16" y1="10.16" x2="10.16" y2="-10.16" width="0.254" layer="94"/>
<wire x1="10.16" y1="-10.16" x2="-10.16" y2="-10.16" width="0.254" layer="94" style="shortdash"/>
<wire x1="-10.16" y1="-10.16" x2="-10.16" y2="10.16" width="0.254" layer="94"/>
<text x="-3.81" y="13.97" size="1.27" layer="94">MAX4466</text>
<text x="-3.81" y="11.43" size="1.27" layer="94">MIC AMP</text>
<text x="-6.985" y="-12.7" size="1.27" layer="94">VCC:</text>
<text x="-0.635" y="-12.7" size="1.27" layer="94">2.4-5.5V</text>
<text x="-6.985" y="-15.24" size="1.27" layer="94">Temp:</text>
<text x="-0.635" y="-15.24" size="1.27" layer="94">-40-85C</text>
<wire x1="-10.16" y1="16.51" x2="10.16" y2="16.51" width="0.254" layer="94"/>
<wire x1="-10.16" y1="16.51" x2="-10.16" y2="10.16" width="0.254" layer="94"/>
<wire x1="10.16" y1="16.51" x2="10.16" y2="10.16" width="0.254" layer="94"/>
<wire x1="-10.16" y1="-10.16" x2="-10.16" y2="-16.51" width="0.254" layer="94"/>
<wire x1="-10.16" y1="-16.51" x2="10.16" y2="-16.51" width="0.254" layer="94"/>
<wire x1="10.16" y1="-16.51" x2="10.16" y2="-10.16" width="0.254" layer="94"/>
<text x="-10.16" y="17.78" size="1.27" layer="95">&gt;NAME</text>
<text x="-10.16" y="-20.32" size="1.27" layer="96">&gt;VALUE</text>
</symbol>
<symbol name="FERRITE">
<text x="-1.27" y="1.905" size="1.27" layer="95">&gt;NAME</text>
<text x="-1.27" y="-3.175" size="1.27" layer="95">&gt;VALUE</text>
<pin name="P$1" x="-2.54" y="0" visible="off" length="short" direction="pas"/>
<pin name="P$2" x="2.54" y="0" visible="off" length="short" direction="pas" rot="R180"/>
<wire x1="-1.27" y1="0.9525" x2="1.27" y2="0.9525" width="0.4064" layer="94"/>
<wire x1="1.27" y1="0.9525" x2="1.27" y2="-0.9525" width="0.4064" layer="94"/>
<wire x1="1.27" y1="-0.9525" x2="-1.27" y2="-0.9525" width="0.4064" layer="94"/>
<wire x1="-1.27" y1="-0.9525" x2="-1.27" y2="0.9525" width="0.4064" layer="94"/>
</symbol>
<symbol name="GND">
<wire x1="-1.27" y1="0" x2="1.27" y2="0" width="0.254" layer="94"/>
<text x="-1.524" y="-2.54" size="1.27" layer="96">&gt;VALUE</text>
<pin name="GND" x="0" y="2.54" visible="off" length="short" direction="sup" rot="R270"/>
</symbol>
<symbol name="VCC">
<text x="-1.524" y="1.016" size="1.27" layer="96">&gt;VALUE</text>
<pin name="VCC" x="0" y="-2.54" visible="off" length="short" direction="sup" rot="R90"/>
<wire x1="-1.27" y1="-1.27" x2="0" y2="0" width="0.254" layer="94"/>
<wire x1="0" y1="0" x2="1.27" y2="-1.27" width="0.254" layer="94"/>
</symbol>
<symbol name="RESISTOR">
<wire x1="-2.54" y1="1.27" x2="2.54" y2="1.27" width="0.254" layer="94"/>
<wire x1="2.54" y1="1.27" x2="2.54" y2="-1.27" width="0.254" layer="94"/>
<wire x1="2.54" y1="-1.27" x2="-2.54" y2="-1.27" width="0.254" layer="94"/>
<wire x1="-2.54" y1="-1.27" x2="-2.54" y2="1.27" width="0.254" layer="94"/>
<text x="-2.54" y="2.032" size="1.27" layer="95" font="vector">&gt;NAME</text>
<text x="-2.54" y="-3.175" size="1.27" layer="96" font="vector">&gt;VALUE</text>
<pin name="1" x="-5.08" y="0" visible="off" length="short" direction="pas" swaplevel="1"/>
<pin name="2" x="5.08" y="0" visible="off" length="short" direction="pas" swaplevel="1" rot="R180"/>
</symbol>
<symbol name="CAPACITOR">
<wire x1="0" y1="0.762" x2="0" y2="0" width="0.1524" layer="94"/>
<wire x1="0" y1="2.54" x2="0" y2="1.778" width="0.1524" layer="94"/>
<text x="2.54" y="2.54" size="1.27" layer="95" font="vector">&gt;NAME</text>
<text x="2.54" y="0" size="1.27" layer="96" font="vector">&gt;VALUE</text>
<rectangle x1="-1.27" y1="0.508" x2="1.27" y2="1.016" layer="94"/>
<rectangle x1="-1.27" y1="1.524" x2="1.27" y2="2.032" layer="94"/>
<pin name="P$1" x="0" y="5.08" visible="off" length="short" direction="pas" swaplevel="1" rot="R270"/>
<pin name="P$2" x="0" y="-2.54" visible="off" length="short" direction="pas" swaplevel="1" rot="R90"/>
</symbol>
<symbol name="AGND">
<wire x1="-1.27" y1="0" x2="1.27" y2="0" width="0.254" layer="94"/>
<text x="-1.524" y="-2.54" size="1.27" layer="96">&gt;VALUE</text>
<pin name="AGND" x="0" y="2.54" visible="off" length="short" direction="sup" rot="R270"/>
</symbol>
<symbol name="AVCC">
<text x="-1.524" y="1.016" size="1.27" layer="96">&gt;VALUE</text>
<pin name="AVCC" x="0" y="-2.54" visible="off" length="short" direction="sup" rot="R90"/>
<wire x1="-1.27" y1="-1.27" x2="0" y2="0" width="0.254" layer="94"/>
<wire x1="0" y1="0" x2="1.27" y2="-1.27" width="0.254" layer="94"/>
</symbol>
<symbol name="POTENTIOMETER">
<wire x1="-0.762" y1="2.54" x2="-0.762" y2="-2.54" width="0.254" layer="94"/>
<wire x1="0.762" y1="-2.54" x2="0.762" y2="2.54" width="0.254" layer="94"/>
<wire x1="2.54" y1="0" x2="1.651" y2="0" width="0.1524" layer="94"/>
<wire x1="1.651" y1="0" x2="-1.8796" y2="1.7526" width="0.1524" layer="94"/>
<wire x1="0.762" y1="2.54" x2="-0.762" y2="2.54" width="0.254" layer="94"/>
<wire x1="-0.762" y1="-2.54" x2="0.762" y2="-2.54" width="0.254" layer="94"/>
<wire x1="-2.1597" y1="1.2939" x2="-3.1989" y2="2.4495" width="0.1524" layer="94"/>
<wire x1="-3.1989" y1="2.4495" x2="-1.7018" y2="2.2352" width="0.1524" layer="94"/>
<wire x1="-2.54" y1="-2.54" x2="-2.54" y2="-0.508" width="0.1524" layer="94"/>
<wire x1="-2.54" y1="-0.508" x2="-3.048" y2="-1.524" width="0.1524" layer="94"/>
<wire x1="-2.54" y1="-0.508" x2="-2.032" y2="-1.524" width="0.1524" layer="94"/>
<wire x1="-2.1597" y1="1.2939" x2="-1.7018" y2="2.2352" width="0.1524" layer="94"/>
<text x="-5.969" y="-3.81" size="1.27" layer="95" rot="R90">&gt;NAME</text>
<text x="-3.81" y="-3.81" size="1.27" layer="96" rot="R90">&gt;VALUE</text>
<pin name="A" x="0" y="-5.08" visible="pad" length="short" direction="pas" rot="R90"/>
<pin name="E" x="0" y="5.08" visible="pad" length="short" direction="pas" rot="R270"/>
<pin name="S" x="5.08" y="0" visible="pad" length="short" direction="pas" rot="R180"/>
</symbol>
</symbols>
<devicesets>
<deviceset name="MAX4466" prefix="U" uservalue="yes">
<description>&lt;p&gt;&lt;b&gt;MAX4466&lt;/b&gt; - Microphone Pre-Amp&lt;/p&gt;</description>
<gates>
<gate name="G$1" symbol="MAX4466" x="0" y="0"/>
</gates>
<devices>
<device name="&quot;&quot;" package="SC70-5">
<connects>
<connect gate="G$1" pin="GND" pad="2"/>
<connect gate="G$1" pin="IN+" pad="1"/>
<connect gate="G$1" pin="IN-" pad="3"/>
<connect gate="G$1" pin="OUT" pad="4"/>
<connect gate="G$1" pin="VCC" pad="5"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="FERRITE" prefix="FB" uservalue="yes">
<description>&lt;p&gt;&lt;b&gt;Ferrite Bead&lt;/b&gt;&lt;/p&gt;
&lt;p&gt;0603&lt;/p&gt;
&lt;ul&gt;
&lt;li&gt;MMZ1608B121C - 120 Ohm @ 100MHz, 600mA, 0.15 Ohm DC Resistance - Digikey: 445-2164-1-ND&lt;/li&gt;
&lt;li&gt;BK1608HW121-T - 120 Ohm, 600mA Ferrite Chip - Digikey: 587-1876-2-ND&lt;/li&gt;
&lt;/ul&gt;
&lt;p&gt;0805&lt;/p&gt;
&lt;ul&gt;
&lt;li&gt;HZ0805B272R-10 - 2.7K Ohm @ 100MHz, 200mA, 0.8 Ohm DC Resistance - Digikey: 240-2504-1-ND (see also Murata BLM21BD272SN1L)&lt;/li&gt;
&lt;li&gt;MMZ2012Y152B - 1.5K Ohm @ 100MHz, 500mA, 0.4 Ohm DC Resistance - Digikey: 445-1560-1-ND - Mainly for high frequency (80-400MHz)&lt;/li&gt;
&lt;li&gt;MMZ2012R102A - 1K Ohm @ 100MHz, 500mA, 0.3 Ohm DC Resistance - Digikey: 445-1555-2-ND - More general purpose (10-200MHz)&lt;/li&gt;
&lt;/ul&gt;</description>
<gates>
<gate name="G$1" symbol="FERRITE" x="0" y="0"/>
</gates>
<devices>
<device name="" package="0603">
<connects>
<connect gate="G$1" pin="P$1" pad="1"/>
<connect gate="G$1" pin="P$2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="0805" package="0805">
<connects>
<connect gate="G$1" pin="P$1" pad="1"/>
<connect gate="G$1" pin="P$2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_0402" package="_0402">
<connects>
<connect gate="G$1" pin="P$1" pad="1"/>
<connect gate="G$1" pin="P$2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_0402MP" package="_0402MP">
<connects>
<connect gate="G$1" pin="P$1" pad="1"/>
<connect gate="G$1" pin="P$2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_0603" package="_0603">
<connects>
<connect gate="G$1" pin="P$1" pad="1"/>
<connect gate="G$1" pin="P$2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_0603MP" package="_0603MP">
<connects>
<connect gate="G$1" pin="P$1" pad="1"/>
<connect gate="G$1" pin="P$2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_0805" package="_0805">
<connects>
<connect gate="G$1" pin="P$1" pad="1"/>
<connect gate="G$1" pin="P$2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_0805MP" package="_0805MP">
<connects>
<connect gate="G$1" pin="P$1" pad="1"/>
<connect gate="G$1" pin="P$2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="GND">
<description>&lt;b&gt;GND&lt;/b&gt;</description>
<gates>
<gate name="G$1" symbol="GND" x="0" y="0"/>
</gates>
<devices>
<device name="">
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="VCC" prefix="P+">
<description>&lt;b&gt;VCC SUPPLY SYMBOL&lt;/b&gt;</description>
<gates>
<gate name="VCC" symbol="VCC" x="0" y="0"/>
</gates>
<devices>
<device name="">
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="RESISTOR" prefix="R" uservalue="yes">
<description>&lt;p&gt;&lt;b&gt;Resistors&lt;/b&gt;&lt;/p&gt;
&lt;b&gt;0402&lt;/b&gt; - 0402 Surface Mount Package
&lt;ul&gt;
&lt;li&gt;22 Ohm 1% 1/16W [Digikey: 311-22.0LRTR-ND]&lt;/li&gt;
&lt;li&gt;33 Ohm 5% 1/16W&lt;/li&gt;
&lt;li&gt;1.0K 5% 1/16W&lt;/li&gt;
&lt;li&gt;1.5K 5% 1/16W&lt;/li&gt;
&lt;li&gt;2.0K 1% 1/16W&lt;/li&gt;
&lt;li&gt;10.0K 1% 1/16W [Digikey: 311-10.0KLRTR-ND]&lt;/li&gt;
&lt;li&gt;10.0K 5% 1/16W [Digikey: RMCF0402JT10K0TR-ND]&lt;/li&gt;
&lt;li&gt;12.1K 1% 1/16W [Digikey: 311-22.0LRTR-ND]&lt;/li&gt;
&lt;li&gt;100.0K 5% 1/16W&lt;/li&gt;
&lt;/ul&gt;
&lt;b&gt;0603&lt;/b&gt; - 0603 Surface Mount Package&lt;br&gt;
&lt;ul&gt;
&lt;li&gt;0 Ohm 1/10 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;15 Ohm 1/10 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;33 Ohm 1/10 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;49.9 Ohm 1/10 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;100 Ohm 1/10 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;150 Ohm 1/10 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;240 Ohm 1/10 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;390 Ohm 1/10 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;560 Ohm 1/10 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;680 Ohm 1/10 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;750 Ohm 1/10 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;1.0K Ohm 1/10 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;1.5K Ohm 1/10 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;2.0K Ohm 1/10 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;2.2K Ohm 1/10 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;3.3K Ohm 1/10 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;4.7K Ohm 1/10 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;10.0K Ohm 1/10 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;12.0K Ohm 1/10 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;12.1K Ohm 1/10 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;20.0K Ohm 1/10 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;33.0K Ohm 1/10 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;100.0K Ohm 1/10 Watt 1% Resistor&lt;/li&gt;
&lt;/ul&gt;
&lt;b&gt;0805&lt;/b&gt; - 0805 Surface Mount Package
&lt;ul&gt;
&lt;li&gt;0 Ohm 1/8 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;33 Ohm 1/8 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;100 Ohm 1/8 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;150 Ohm 1/8 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;200 Ohm 1/8 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;240 Ohm 1/8 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;330 Ohm 1/8 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;390 Ohm 1/8 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;470 Ohm 1/8 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;1.0K Ohm 1/8 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;1.5K Ohm 1/8 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;2.0K Ohm 1/8 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;4.7K Ohm 1/8 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;5.1K Ohm 1/8 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;5.6K Ohm 1/8 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;10.0K Ohm 1/8 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;22.0K Ohm 1/8 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;33.0K Ohm 1/8 Watt 1% Resistor&lt;/li&gt;
&lt;li&gt;100K Ohm 1/8 Watt 1% Resistor&lt;/li&gt;
&lt;/ul&gt;
&lt;b&gt;1206&lt;/b&gt; - 1206 Surface Mount Package&lt;br/&gt;
&lt;br/&gt;
&lt;b&gt;2012&lt;/b&gt; - 2010 Surface Mount Package&lt;br/&gt;
&lt;ul&gt;&lt;li&gt;0.11 Ohm 1/2 Watt 1% Resistor - Digikey: RHM.11UCT-ND&lt;/li&gt;&lt;/ul&gt;</description>
<gates>
<gate name="G$1" symbol="RESISTOR" x="0" y="0"/>
</gates>
<devices>
<device name="0805" package="0805">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="1206" package="1206">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="0603" package="0603">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="0402" package="0402">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="0603MINI" package="0603-MINI">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="2012" package="2012">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="0805_NOTHERMALS" package="0805_NOTHERMALS">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="2512" package="2512">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_0402" package="_0402">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_0402MP" package="_0402MP">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_0603" package="_0603">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_0603MP" package="_0603MP">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_0805" package="_0805">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_0805MP" package="_0805MP">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="CAP_CERAMIC" prefix="C" uservalue="yes">
<description>&lt;p&gt;&lt;b&gt;Ceramic Capacitors&lt;/b&gt;&lt;/p&gt;
&lt;b&gt;0402&lt;/b&gt; - 0402 Surface Mount Capacitors
&lt;ul&gt;
&lt;li&gt;16pF 50V 5% [Digikey: 445-4899-2-ND]&lt;/li&gt;
&lt;li&gt;18pF 50V 5% [Digikey: 490-1281-2-ND]&lt;/li&gt;
&lt;li&gt;22pF 50V 5% [Digikey: 490-1283-2-ND]&lt;/li&gt;
&lt;li&gt;68pF 50V 5% [Digikey: 490-1289-2-ND]&lt;/li&gt;
&lt;li&gt;0.1uF 10V 10% [Digikey: 490-1318-2-ND]&lt;/li&gt;
&lt;li&gt;1.0uF 6.3V 10% [Digikey: 490-1320-2-ND]&lt;/li&gt;
&lt;/ul&gt;
&lt;b&gt;0603&lt;/b&gt; - 0603 Surface Mount Capacitors
&lt;ul&gt;
&lt;li&gt;16 pF 50V 5% [Digikey: 445-5051-2-ND]&lt;/li&gt;
&lt;li&gt;22 pF 50V [Digikey: PCC220ACVTR-ND]&lt;/li&gt;
&lt;li&gt;33 pF 50V 5% [Digikey: 490-1415-1-ND]&lt;/li&gt;
&lt;li&gt;56pF 50V 5% [Digikey: 490-1421-1-ND]&lt;/li&gt;
&lt;li&gt;220pF 50V 5% [Digikey: 445-1285-1-ND]&lt;/li&gt;
&lt;li&gt;680 pF 50V &lt;/li&gt;
&lt;li&gt;2200 pF 50V 5% C0G [Digikey: 445-1297-1-ND]&lt;/li&gt;
&lt;li&gt;5600 pF 100V 5% X7R [Digikey: 478-3711-1-ND]&lt;/li&gt;
&lt;li&gt;0.1 µF 25V 10% [Digikey: PCC2277TR-ND]&lt;/li&gt;
&lt;li&gt;0.22 µF 16V 10% X7R [Digikey: 445-1318-1-ND]&lt;/li&gt;
&lt;li&gt;1.0 µF 25V 10% [Digikey: 445-5146-2-ND]&lt;/li&gt;
&lt;/ul&gt;
&lt;b&gt;0603&lt;/b&gt; - RF Specific
&lt;ul&gt;
&lt;li&gt;3pF 250V +/-0.1pF RF [Digikey: 712-1347-1-ND]&lt;/li&gt;
&lt;li&gt;18 pF 250V 5%  [Digikey: 478-3505-1-ND or 712-1322-1-ND]&lt;/li&gt;
&lt;li&gt;56 pF 250V 5% C0G RF [Digikey: 490-4867-1-ND]&lt;/li&gt;
&lt;li&gt;68 pF 250V RF [Digikey: 490-4868-1-ND]&lt;/li&gt;
&lt;/ul&gt;
&lt;b&gt;0805&lt;/b&gt; - 0805 Surface Mount Capacitors
&lt;ul&gt;
&lt;li&gt;220 pF 250V 2% &lt;strong&gt;RF&lt;/strong&gt; Ceramic Capacitor [Digikey: 712-1398-1-ND]&lt;/li&gt;
&lt;li&gt;1000 pF 50V 2% NP0 Ceramic Capacitor [Digikey: 478-3760-1-ND]&lt;/li&gt;
&lt;li&gt;0.1 µF 25V 10% Ceramic Capacitor [Digikey: PCC1828TR-ND]&lt;/li&gt;
&lt;li&gt;1.0 µF 16V 10% Ceramic Capacitor[Digikey: 490-1691-2-ND]&lt;/li&gt;
&lt;li&gt;10.0 µF 10V 10% Ceramic Capacitor[Digikey: 709-1228-1-ND]&lt;/li&gt;
&lt;li&gt;10.0 uF 16V 10% Ceramic Capacitor [Digikey: 478-5165-2-ND]&lt;/li&gt;
&lt;li&gt;47 uF 6.3V 20% Ceramic Capacitor [Digikey: 587-1779-1-ND or 399-5506-1-ND]&lt;/li&gt;
&lt;/ul&gt;
&lt;/ul&gt;&lt;b&gt;1206&lt;/b&gt; - 1206 Surface Mount Capacitors
&lt;ul&gt;
&lt;li&gt;47uF 10V 20% Ceramic Capacitor [Digikey: 490-5528-1-ND or 399-5508-1-ND or 445-6010-1-ND]&lt;/li&gt;
&lt;li&gt;100uF 6.3V -20%, +80% Y5V Ceramic Capacitor (Digikey: 490-4512-1-ND, Mouser: 81-GRM31CF50J107ZE1L)&lt;/li&gt;
&lt;/ul&gt;</description>
<gates>
<gate name="G$1" symbol="CAPACITOR" x="0" y="-2.54"/>
</gates>
<devices>
<device name="0805" package="0805">
<connects>
<connect gate="G$1" pin="P$1" pad="1"/>
<connect gate="G$1" pin="P$2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="1206" package="1206">
<connects>
<connect gate="G$1" pin="P$1" pad="1"/>
<connect gate="G$1" pin="P$2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="0603" package="0603">
<connects>
<connect gate="G$1" pin="P$1" pad="1"/>
<connect gate="G$1" pin="P$2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="0402" package="0402">
<connects>
<connect gate="G$1" pin="P$1" pad="1"/>
<connect gate="G$1" pin="P$2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="0603MINI" package="0603-MINI">
<connects>
<connect gate="G$1" pin="P$1" pad="1"/>
<connect gate="G$1" pin="P$2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="0805-NOTHERMALS" package="0805_NOTHERMALS">
<connects>
<connect gate="G$1" pin="P$1" pad="1"/>
<connect gate="G$1" pin="P$2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_0402" package="_0402">
<connects>
<connect gate="G$1" pin="P$1" pad="1"/>
<connect gate="G$1" pin="P$2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_0402MP" package="_0402MP">
<connects>
<connect gate="G$1" pin="P$1" pad="1"/>
<connect gate="G$1" pin="P$2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_0603" package="_0603">
<connects>
<connect gate="G$1" pin="P$1" pad="1"/>
<connect gate="G$1" pin="P$2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_0603MP" package="_0603MP">
<connects>
<connect gate="G$1" pin="P$1" pad="1"/>
<connect gate="G$1" pin="P$2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_0805" package="_0805">
<connects>
<connect gate="G$1" pin="P$1" pad="1"/>
<connect gate="G$1" pin="P$2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_0805MP" package="_0805MP">
<connects>
<connect gate="G$1" pin="P$1" pad="1"/>
<connect gate="G$1" pin="P$2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="AGND">
<description>&lt;b&gt;Analog GND&lt;/b&gt;</description>
<gates>
<gate name="G$1" symbol="AGND" x="0" y="0"/>
</gates>
<devices>
<device name="">
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="AVCC">
<description>&lt;b&gt;Analog VCC&lt;/b&gt;</description>
<gates>
<gate name="G$1" symbol="AVCC" x="0" y="0"/>
</gates>
<devices>
<device name="">
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="TRIMPOT" prefix="VR" uservalue="yes">
<description>&lt;p&gt;&lt;b&gt;3-Pin SMT Trimpots&lt;/b&gt;&lt;/p&gt;


&lt;p&gt;&lt;b&gt;Bourns TC33 (X-2) Series&lt;/b&gt;&lt;/p&gt;
&lt;ul&gt;
&lt;li&gt; 10K - Digikey: TC33X-2-103E&lt;/li&gt;
&lt;li&gt; 100K - Digikey: TC33X-104ECT-ND&lt;/li&gt;
&lt;/ul&gt;

&lt;p&gt;&lt;b&gt;Bourns 3303 (W) Series&lt;/b&gt;&lt;/p&gt;
&lt;ul&gt;
&lt;li&gt; 3mm 10K Single Turn - Digikey: 3303W-103ETR-ND&lt;/li&gt;
&lt;li&gt; 3mm 100K Single Turn - Digikey: 3303X-104ETR-ND&lt;/li&gt;
&lt;/ul&gt;</description>
<gates>
<gate name="G$1" symbol="POTENTIOMETER" x="0" y="0"/>
</gates>
<devices>
<device name="3303W/X" package="TRIMPOT_BOURNS_3303W">
<connects>
<connect gate="G$1" pin="A" pad="1"/>
<connect gate="G$1" pin="E" pad="3"/>
<connect gate="G$1" pin="S" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="TC33X-2" package="TRIMPOT_BOURNS_TC33X-2">
<connects>
<connect gate="G$1" pin="A" pad="1"/>
<connect gate="G$1" pin="E" pad="3"/>
<connect gate="G$1" pin="S" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
<library name="adafruit">
<packages>
<package name="FEATHERWING">
<wire x1="2.54" y1="0" x2="48.26" y2="0" width="0" layer="20"/>
<wire x1="48.26" y1="0" x2="50.8" y2="2.54" width="0" layer="20" curve="90"/>
<wire x1="50.8" y1="2.54" x2="50.8" y2="20.32" width="0" layer="20"/>
<wire x1="50.8" y1="20.32" x2="48.26" y2="22.86" width="0" layer="20" curve="90"/>
<wire x1="48.26" y1="22.86" x2="2.54" y2="22.86" width="0" layer="20"/>
<wire x1="2.54" y1="22.86" x2="0" y2="20.32" width="0" layer="20" curve="90"/>
<wire x1="0" y1="20.32" x2="0" y2="2.54" width="0" layer="20"/>
<wire x1="0" y1="2.54" x2="2.54" y2="0" width="0" layer="20" curve="90"/>
<hole x="48.26" y="20.32" drill="2.54"/>
<hole x="48.26" y="2.54" drill="2.54"/>
<pad name="P$1" x="2.54" y="20.32" drill="2.5" diameter="3.81"/>
<pad name="P$2" x="2.54" y="2.54" drill="2.5" diameter="3.81"/>
<pad name="28" x="16.51" y="21.59" drill="1" diameter="1.778"/>
<pad name="27" x="19.05" y="21.59" drill="1" diameter="1.778"/>
<pad name="26" x="21.59" y="21.59" drill="1" diameter="1.778"/>
<pad name="25" x="24.13" y="21.59" drill="1" diameter="1.778"/>
<pad name="24" x="26.67" y="21.59" drill="1" diameter="1.778"/>
<pad name="23" x="29.21" y="21.59" drill="1" diameter="1.778"/>
<pad name="22" x="31.75" y="21.59" drill="1" diameter="1.778"/>
<pad name="21" x="34.29" y="21.59" drill="1" diameter="1.778"/>
<pad name="20" x="36.83" y="21.59" drill="1" diameter="1.778"/>
<pad name="19" x="39.37" y="21.59" drill="1" diameter="1.778"/>
<pad name="18" x="41.91" y="21.59" drill="1" diameter="1.778"/>
<pad name="17" x="44.45" y="21.59" drill="1" diameter="1.778"/>
<pad name="5" x="16.51" y="1.27" drill="1" diameter="1.778"/>
<pad name="6" x="19.05" y="1.27" drill="1" diameter="1.778"/>
<pad name="7" x="21.59" y="1.27" drill="1" diameter="1.778"/>
<pad name="8" x="24.13" y="1.27" drill="1" diameter="1.778"/>
<pad name="9" x="26.67" y="1.27" drill="1" diameter="1.778"/>
<pad name="10" x="29.21" y="1.27" drill="1" diameter="1.778"/>
<pad name="11" x="31.75" y="1.27" drill="1" diameter="1.778"/>
<pad name="12" x="34.29" y="1.27" drill="1" diameter="1.778"/>
<pad name="13" x="36.83" y="1.27" drill="1" diameter="1.778"/>
<pad name="14" x="39.37" y="1.27" drill="1" diameter="1.778"/>
<pad name="15" x="41.91" y="1.27" drill="1" diameter="1.778"/>
<pad name="16" x="44.45" y="1.27" drill="1" diameter="1.778"/>
<pad name="4" x="13.97" y="1.27" drill="1" diameter="1.778"/>
<pad name="3" x="11.43" y="1.27" drill="1" diameter="1.778"/>
<pad name="2" x="8.89" y="1.27" drill="1" diameter="1.778"/>
<pad name="1" x="6.35" y="1.27" drill="1" diameter="1.778"/>
</package>
<package name="FEATHERWING_DIM">
<wire x1="2.54" y1="0" x2="48.26" y2="0" width="0" layer="21"/>
<wire x1="48.26" y1="0" x2="50.8" y2="2.54" width="0" layer="21" curve="90"/>
<wire x1="50.8" y1="2.54" x2="50.8" y2="20.32" width="0" layer="21"/>
<wire x1="50.8" y1="20.32" x2="48.26" y2="22.86" width="0" layer="21" curve="90"/>
<wire x1="48.26" y1="22.86" x2="2.54" y2="22.86" width="0" layer="21"/>
<wire x1="2.54" y1="22.86" x2="0" y2="20.32" width="0" layer="21" curve="90"/>
<wire x1="0" y1="20.32" x2="0" y2="13.716" width="0" layer="21"/>
<wire x1="0" y1="13.716" x2="0.508" y2="13.208" width="0" layer="21"/>
<wire x1="0.508" y1="13.208" x2="0.508" y2="9.652" width="0" layer="21"/>
<wire x1="0.508" y1="9.652" x2="0" y2="9.144" width="0" layer="21"/>
<wire x1="0" y1="9.144" x2="0" y2="2.54" width="0" layer="21"/>
<wire x1="0" y1="2.54" x2="2.54" y2="0" width="0" layer="21" curve="90"/>
<hole x="48.26" y="20.32" drill="2.54"/>
<hole x="48.26" y="2.54" drill="2.54"/>
<pad name="P$1" x="2.54" y="20.32" drill="2.5" diameter="3.81"/>
<pad name="P$2" x="2.54" y="2.54" drill="2.5" diameter="3.81"/>
<pad name="28" x="16.51" y="21.59" drill="1" diameter="1.778"/>
<pad name="27" x="19.05" y="21.59" drill="1" diameter="1.778"/>
<pad name="26" x="21.59" y="21.59" drill="1" diameter="1.778"/>
<pad name="25" x="24.13" y="21.59" drill="1" diameter="1.778"/>
<pad name="24" x="26.67" y="21.59" drill="1" diameter="1.778"/>
<pad name="23" x="29.21" y="21.59" drill="1" diameter="1.778"/>
<pad name="22" x="31.75" y="21.59" drill="1" diameter="1.778"/>
<pad name="21" x="34.29" y="21.59" drill="1" diameter="1.778"/>
<pad name="20" x="36.83" y="21.59" drill="1" diameter="1.778"/>
<pad name="19" x="39.37" y="21.59" drill="1" diameter="1.778"/>
<pad name="18" x="41.91" y="21.59" drill="1" diameter="1.778"/>
<pad name="17" x="44.45" y="21.59" drill="1" diameter="1.778"/>
<pad name="5" x="16.51" y="1.27" drill="1" diameter="1.778"/>
<pad name="6" x="19.05" y="1.27" drill="1" diameter="1.778"/>
<pad name="7" x="21.59" y="1.27" drill="1" diameter="1.778"/>
<pad name="8" x="24.13" y="1.27" drill="1" diameter="1.778"/>
<pad name="9" x="26.67" y="1.27" drill="1" diameter="1.778"/>
<pad name="10" x="29.21" y="1.27" drill="1" diameter="1.778"/>
<pad name="11" x="31.75" y="1.27" drill="1" diameter="1.778"/>
<pad name="12" x="34.29" y="1.27" drill="1" diameter="1.778"/>
<pad name="13" x="36.83" y="1.27" drill="1" diameter="1.778"/>
<pad name="14" x="39.37" y="1.27" drill="1" diameter="1.778"/>
<pad name="15" x="41.91" y="1.27" drill="1" diameter="1.778"/>
<pad name="16" x="44.45" y="1.27" drill="1" diameter="1.778"/>
<pad name="4" x="13.97" y="1.27" drill="1" diameter="1.778"/>
<pad name="3" x="11.43" y="1.27" drill="1" diameter="1.778"/>
<pad name="2" x="8.89" y="1.27" drill="1" diameter="1.778"/>
<pad name="1" x="6.35" y="1.27" drill="1" diameter="1.778"/>
</package>
</packages>
<symbols>
<symbol name="MICROSHIELD">
<wire x1="0" y1="33.02" x2="0" y2="22.86" width="0.254" layer="94"/>
<wire x1="0" y1="22.86" x2="0" y2="12.7" width="0.254" layer="94"/>
<wire x1="0" y1="12.7" x2="0" y2="0" width="0.254" layer="94"/>
<wire x1="0" y1="0" x2="48.26" y2="0" width="0.254" layer="94"/>
<wire x1="48.26" y1="0" x2="48.26" y2="33.02" width="0.254" layer="94"/>
<wire x1="48.26" y1="33.02" x2="12.7" y2="33.02" width="0.254" layer="94"/>
<pin name="!RESET" x="5.08" y="-5.08" length="middle" direction="in" rot="R90"/>
<pin name="3V" x="7.62" y="-5.08" length="middle" direction="sup" rot="R90"/>
<pin name="AREF" x="10.16" y="-5.08" length="middle" direction="pas" rot="R90"/>
<pin name="GND" x="12.7" y="-5.08" length="middle" direction="pwr" rot="R90"/>
<pin name="GPIOA0" x="15.24" y="-5.08" length="middle" rot="R90"/>
<pin name="GPIOA1" x="17.78" y="-5.08" length="middle" rot="R90"/>
<pin name="GPIOA2" x="20.32" y="-5.08" length="middle" rot="R90"/>
<pin name="GPIOA3" x="22.86" y="-5.08" length="middle" rot="R90"/>
<pin name="GPIOA4" x="25.4" y="-5.08" length="middle" rot="R90"/>
<pin name="GPIOA5" x="27.94" y="-5.08" length="middle" rot="R90"/>
<pin name="GPIOSCK" x="30.48" y="-5.08" length="middle" rot="R90"/>
<pin name="GPIOMOSI" x="33.02" y="-5.08" length="middle" rot="R90"/>
<pin name="GPIOMISO" x="35.56" y="-5.08" length="middle" rot="R90"/>
<pin name="GPIORX" x="38.1" y="-5.08" length="middle" rot="R90"/>
<pin name="GPIOTX" x="40.64" y="-5.08" length="middle" rot="R90"/>
<pin name="NC" x="43.18" y="-5.08" length="middle" direction="pas" rot="R90"/>
<pin name="GPIOSDA" x="43.18" y="38.1" length="middle" rot="R270"/>
<pin name="GPIOSCL" x="40.64" y="38.1" length="middle" rot="R270"/>
<circle x="45.72" y="30.48" radius="1.27" width="0.254" layer="94"/>
<circle x="45.72" y="2.54" radius="1.27" width="0.254" layer="94"/>
<pin name="GPIO5" x="38.1" y="38.1" length="middle" rot="R270"/>
<pin name="GPIO9" x="33.02" y="38.1" length="middle" rot="R270"/>
<pin name="GPIO6" x="35.56" y="38.1" length="middle" rot="R270"/>
<pin name="GPIO10" x="30.48" y="38.1" length="middle" rot="R270"/>
<pin name="GPIO11" x="27.94" y="38.1" length="middle" rot="R270"/>
<pin name="GPIO12" x="25.4" y="38.1" length="middle" rot="R270"/>
<pin name="GPIO13" x="22.86" y="38.1" length="middle" rot="R270"/>
<pin name="EN" x="17.78" y="38.1" length="middle" direction="pas" rot="R270"/>
<pin name="USB" x="20.32" y="38.1" length="middle" direction="sup" rot="R270"/>
<pin name="VBAT" x="15.24" y="38.1" length="middle" direction="sup" rot="R270"/>
<wire x1="12.7" y1="33.02" x2="5.08" y2="33.02" width="0.254" layer="94"/>
<wire x1="5.08" y1="33.02" x2="0" y2="33.02" width="0.254" layer="94"/>
<wire x1="5.08" y1="33.02" x2="5.08" y2="25.4" width="0.254" layer="94"/>
<wire x1="5.08" y1="25.4" x2="7.62" y2="25.4" width="0.254" layer="94"/>
<wire x1="7.62" y1="25.4" x2="10.16" y2="25.4" width="0.254" layer="94"/>
<wire x1="10.16" y1="25.4" x2="12.7" y2="25.4" width="0.254" layer="94"/>
<wire x1="12.7" y1="25.4" x2="12.7" y2="33.02" width="0.254" layer="94"/>
<wire x1="7.62" y1="27.94" x2="7.62" y2="25.4" width="0.254" layer="94"/>
<wire x1="10.16" y1="27.94" x2="10.16" y2="25.4" width="0.254" layer="94"/>
<wire x1="0" y1="22.86" x2="5.08" y2="22.86" width="0.254" layer="94"/>
<wire x1="5.08" y1="22.86" x2="5.08" y2="12.7" width="0.254" layer="94"/>
<wire x1="5.08" y1="12.7" x2="0" y2="12.7" width="0.254" layer="94"/>
<circle x="2.54" y="2.54" radius="1.27" width="0.254" layer="94"/>
<circle x="2.54" y="30.48" radius="1.27" width="0.254" layer="94"/>
</symbol>
</symbols>
<devicesets>
<deviceset name="FEATHERWING" prefix="MS">
<gates>
<gate name="G$1" symbol="MICROSHIELD" x="-25.4" y="-15.24"/>
</gates>
<devices>
<device name="" package="FEATHERWING">
<connects>
<connect gate="G$1" pin="!RESET" pad="1"/>
<connect gate="G$1" pin="3V" pad="2"/>
<connect gate="G$1" pin="AREF" pad="3"/>
<connect gate="G$1" pin="EN" pad="27"/>
<connect gate="G$1" pin="GND" pad="4"/>
<connect gate="G$1" pin="GPIO10" pad="22"/>
<connect gate="G$1" pin="GPIO11" pad="23"/>
<connect gate="G$1" pin="GPIO12" pad="24"/>
<connect gate="G$1" pin="GPIO13" pad="25"/>
<connect gate="G$1" pin="GPIO5" pad="19"/>
<connect gate="G$1" pin="GPIO6" pad="20"/>
<connect gate="G$1" pin="GPIO9" pad="21"/>
<connect gate="G$1" pin="GPIOA0" pad="5"/>
<connect gate="G$1" pin="GPIOA1" pad="6"/>
<connect gate="G$1" pin="GPIOA2" pad="7"/>
<connect gate="G$1" pin="GPIOA3" pad="8"/>
<connect gate="G$1" pin="GPIOA4" pad="9"/>
<connect gate="G$1" pin="GPIOA5" pad="10"/>
<connect gate="G$1" pin="GPIOMISO" pad="13"/>
<connect gate="G$1" pin="GPIOMOSI" pad="12"/>
<connect gate="G$1" pin="GPIORX" pad="14"/>
<connect gate="G$1" pin="GPIOSCK" pad="11"/>
<connect gate="G$1" pin="GPIOSCL" pad="18"/>
<connect gate="G$1" pin="GPIOSDA" pad="17"/>
<connect gate="G$1" pin="GPIOTX" pad="15"/>
<connect gate="G$1" pin="NC" pad="16"/>
<connect gate="G$1" pin="USB" pad="26"/>
<connect gate="G$1" pin="VBAT" pad="28"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_NODIM" package="FEATHERWING_DIM">
<connects>
<connect gate="G$1" pin="!RESET" pad="1"/>
<connect gate="G$1" pin="3V" pad="2"/>
<connect gate="G$1" pin="AREF" pad="3"/>
<connect gate="G$1" pin="EN" pad="27"/>
<connect gate="G$1" pin="GND" pad="4"/>
<connect gate="G$1" pin="GPIO10" pad="22"/>
<connect gate="G$1" pin="GPIO11" pad="23"/>
<connect gate="G$1" pin="GPIO12" pad="24"/>
<connect gate="G$1" pin="GPIO13" pad="25"/>
<connect gate="G$1" pin="GPIO5" pad="19"/>
<connect gate="G$1" pin="GPIO6" pad="20"/>
<connect gate="G$1" pin="GPIO9" pad="21"/>
<connect gate="G$1" pin="GPIOA0" pad="5"/>
<connect gate="G$1" pin="GPIOA1" pad="6"/>
<connect gate="G$1" pin="GPIOA2" pad="7"/>
<connect gate="G$1" pin="GPIOA3" pad="8"/>
<connect gate="G$1" pin="GPIOA4" pad="9"/>
<connect gate="G$1" pin="GPIOA5" pad="10"/>
<connect gate="G$1" pin="GPIOMISO" pad="13"/>
<connect gate="G$1" pin="GPIOMOSI" pad="12"/>
<connect gate="G$1" pin="GPIORX" pad="14"/>
<connect gate="G$1" pin="GPIOSCK" pad="11"/>
<connect gate="G$1" pin="GPIOSCL" pad="18"/>
<connect gate="G$1" pin="GPIOSDA" pad="17"/>
<connect gate="G$1" pin="GPIOTX" pad="15"/>
<connect gate="G$1" pin="NC" pad="16"/>
<connect gate="G$1" pin="USB" pad="26"/>
<connect gate="G$1" pin="VBAT" pad="28"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
<library name="supply1" urn="urn:adsk.eagle:library:371">
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
<symbol name="GND" urn="urn:adsk.eagle:symbol:26925/1" library_version="1">
<wire x1="-1.905" y1="0" x2="1.905" y2="0" width="0.254" layer="94"/>
<text x="-2.54" y="-2.54" size="1.778" layer="96">&gt;VALUE</text>
<pin name="GND" x="0" y="2.54" visible="off" length="short" direction="sup" rot="R270"/>
</symbol>
<symbol name="VCC" urn="urn:adsk.eagle:symbol:26928/1" library_version="1">
<wire x1="1.27" y1="-1.905" x2="0" y2="0" width="0.254" layer="94"/>
<wire x1="0" y1="0" x2="-1.27" y2="-1.905" width="0.254" layer="94"/>
<text x="-2.54" y="-2.54" size="1.778" layer="96" rot="R90">&gt;VALUE</text>
<pin name="VCC" x="0" y="-2.54" visible="off" length="short" direction="sup" rot="R90"/>
</symbol>
</symbols>
<devicesets>
<deviceset name="GND" urn="urn:adsk.eagle:component:26954/1" prefix="GND" library_version="1">
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
<deviceset name="VCC" urn="urn:adsk.eagle:component:26957/1" prefix="P+" library_version="1">
<description>&lt;b&gt;SUPPLY SYMBOL&lt;/b&gt;</description>
<gates>
<gate name="VCC" symbol="VCC" x="0" y="0"/>
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
<library name="MJ-3502N">
<packages>
<package name="CUI_MJ-3502N">
<wire x1="-8" y1="4" x2="7" y2="4" width="0.05" layer="39"/>
<wire x1="7" y1="4" x2="7" y2="-4" width="0.05" layer="39"/>
<wire x1="7" y1="-4" x2="-8" y2="-4" width="0.05" layer="39"/>
<wire x1="-8" y1="-4" x2="-8" y2="-3" width="0.05" layer="39"/>
<wire x1="-8" y1="-3" x2="-12" y2="-3" width="0.05" layer="39"/>
<wire x1="-12" y1="-3" x2="-12" y2="3" width="0.05" layer="39"/>
<wire x1="-12" y1="3" x2="-8" y2="3" width="0.05" layer="39"/>
<wire x1="-8" y1="3" x2="-8" y2="4" width="0.05" layer="39"/>
<text x="-7.002359375" y="4.25143125" size="1.27043125" layer="25">&gt;NAME</text>
<text x="-7.106690625" y="-5.55523125" size="1.2712" layer="27">&gt;VALUE</text>
<wire x1="-6.15" y1="-0.65" x2="-5.55" y2="-1.25" width="0.0001" layer="46" curve="90"/>
<wire x1="-5.55" y1="-1.25" x2="-4.95" y2="-0.65" width="0.0001" layer="46" curve="90"/>
<wire x1="-4.95" y1="-0.65" x2="-4.95" y2="0.65" width="0.0001" layer="46"/>
<wire x1="-4.95" y1="0.65" x2="-5.55" y2="1.25" width="0.0001" layer="46" curve="90"/>
<wire x1="-5.55" y1="1.25" x2="-6.15" y2="0.65" width="0.0001" layer="46" curve="90"/>
<wire x1="-6.15" y1="0.65" x2="-6.15" y2="-0.65" width="0.0001" layer="46"/>
<wire x1="-6.75" y1="3.75" x2="6.75" y2="3.75" width="0.127" layer="51"/>
<wire x1="6.75" y1="3.75" x2="6.75" y2="-3.75" width="0.127" layer="51"/>
<wire x1="6.75" y1="-3.75" x2="-6.75" y2="-3.75" width="0.127" layer="51"/>
<wire x1="-6.75" y1="-3.75" x2="-6.75" y2="-3.5" width="0.127" layer="51"/>
<wire x1="-6.75" y1="-3.5" x2="-6.75" y2="3.5" width="0.127" layer="51"/>
<wire x1="-6.75" y1="3.5" x2="-6.75" y2="3.75" width="0.127" layer="51"/>
<wire x1="-6.75" y1="3.75" x2="6.75" y2="3.75" width="0.127" layer="21"/>
<wire x1="6.75" y1="3.75" x2="6.75" y2="-3.75" width="0.127" layer="21"/>
<wire x1="6.75" y1="-3.75" x2="-6.75" y2="-3.75" width="0.127" layer="21"/>
<wire x1="-6.75" y1="-3.75" x2="-6.75" y2="-3.5" width="0.127" layer="21"/>
<wire x1="-6.75" y1="-3.5" x2="-6.75" y2="3.5" width="0.127" layer="21"/>
<wire x1="-6.75" y1="3.5" x2="-6.75" y2="3.75" width="0.127" layer="21"/>
<wire x1="4.95" y1="-0.65" x2="5.55" y2="-1.25" width="0.0001" layer="46" curve="90"/>
<wire x1="5.55" y1="-1.25" x2="6.15" y2="-0.65" width="0.0001" layer="46" curve="90"/>
<wire x1="6.15" y1="-0.65" x2="6.15" y2="0.65" width="0.0001" layer="46"/>
<wire x1="6.15" y1="0.65" x2="5.55" y2="1.25" width="0.0001" layer="46" curve="90"/>
<wire x1="5.55" y1="1.25" x2="4.95" y2="0.65" width="0.0001" layer="46" curve="90"/>
<wire x1="4.95" y1="0.65" x2="4.95" y2="-0.65" width="0.0001" layer="46"/>
<wire x1="-0.75" y1="-0.65" x2="-0.15" y2="-1.25" width="0.0001" layer="46" curve="90"/>
<wire x1="-0.15" y1="-1.25" x2="0.45" y2="-0.65" width="0.0001" layer="46" curve="90"/>
<wire x1="0.45" y1="-0.65" x2="0.45" y2="0.65" width="0.0001" layer="46"/>
<wire x1="0.45" y1="0.65" x2="-0.15" y2="1.25" width="0.0001" layer="46" curve="90"/>
<wire x1="-0.15" y1="1.25" x2="-0.75" y2="0.65" width="0.0001" layer="46" curve="90"/>
<wire x1="-0.75" y1="0.65" x2="-0.75" y2="-0.65" width="0.0001" layer="46"/>
<wire x1="-6.75" y1="3.5" x2="-7.75" y2="3.5" width="0.127" layer="21"/>
<wire x1="-7.75" y1="3.5" x2="-7.75" y2="2.75" width="0.127" layer="21"/>
<wire x1="-7.75" y1="2.75" x2="-7.75" y2="-2.75" width="0.127" layer="21"/>
<wire x1="-7.75" y1="-2.75" x2="-7.75" y2="-3.5" width="0.127" layer="21"/>
<wire x1="-7.75" y1="-3.5" x2="-6.75" y2="-3.5" width="0.127" layer="21"/>
<wire x1="-6.75" y1="3.5" x2="-7.75" y2="3.5" width="0.127" layer="51"/>
<wire x1="-7.75" y1="3.5" x2="-7.75" y2="2.75" width="0.127" layer="51"/>
<wire x1="-7.75" y1="2.75" x2="-7.75" y2="-3.5" width="0.127" layer="51"/>
<wire x1="-7.75" y1="-3.5" x2="-6.75" y2="-3.5" width="0.127" layer="51"/>
<wire x1="-7.75" y1="2.75" x2="-11.75" y2="2.75" width="0.127" layer="51"/>
<wire x1="-11.75" y1="2.75" x2="-11.75" y2="-2.75" width="0.127" layer="51"/>
<wire x1="-11.75" y1="-2.75" x2="-7.8" y2="-2.75" width="0.127" layer="51"/>
<wire x1="-7.75" y1="2.75" x2="-11.75" y2="2.75" width="0.127" layer="21"/>
<wire x1="-11.75" y1="2.75" x2="-11.75" y2="-2.75" width="0.127" layer="21"/>
<wire x1="-11.75" y1="-2.75" x2="-7.75" y2="-2.75" width="0.127" layer="21"/>
<circle x="-8.55" y="3.5" radius="0.1" width="0.2" layer="21"/>
<pad name="1" x="-5.55" y="0" drill="1.2" shape="long" rot="R90"/>
<pad name="2" x="-0.15" y="0" drill="1.2" shape="long" rot="R90"/>
<pad name="3" x="5.55" y="0" drill="1.2" shape="long" rot="R90"/>
</package>
</packages>
<symbols>
<symbol name="MJ-3502N">
<wire x1="-3.556" y1="0.508" x2="-3.556" y2="-2.54" width="0.254" layer="94"/>
<wire x1="-3.556" y1="-2.54" x2="-1.524" y2="-2.54" width="0.254" layer="94"/>
<wire x1="-1.524" y1="-2.54" x2="-1.524" y2="0.508" width="0.254" layer="94"/>
<wire x1="-1.524" y1="0.508" x2="-2.54" y2="0.508" width="0.254" layer="94"/>
<wire x1="-2.54" y1="0.508" x2="-3.556" y2="0.508" width="0.254" layer="94"/>
<wire x1="-2.54" y1="0.508" x2="-2.54" y2="2.54" width="0.254" layer="94"/>
<wire x1="-2.54" y1="2.54" x2="7.62" y2="2.54" width="0.254" layer="94"/>
<wire x1="0" y1="-2.54" x2="1.27" y2="0" width="0.254" layer="94"/>
<wire x1="1.27" y1="0" x2="2.54" y2="-2.54" width="0.254" layer="94"/>
<wire x1="2.54" y1="-2.54" x2="5.08" y2="-2.54" width="0.254" layer="94"/>
<wire x1="5.08" y1="-2.54" x2="7.62" y2="-2.54" width="0.254" layer="94"/>
<wire x1="4.572" y1="-0.762" x2="5.08" y2="-2.54" width="0.254" layer="94"/>
<wire x1="5.08" y1="-2.54" x2="5.588" y2="-0.762" width="0.254" layer="94"/>
<wire x1="5.588" y1="-0.762" x2="5.08" y2="-0.762" width="0.254" layer="94"/>
<polygon width="0.254" layer="94">
<vertex x="5.588" y="-0.762"/>
<vertex x="4.572" y="-0.762"/>
<vertex x="5.08" y="-2.54"/>
</polygon>
<wire x1="5.08" y1="-0.762" x2="4.572" y2="-0.762" width="0.254" layer="94"/>
<wire x1="7.62" y1="5.08" x2="7.62" y2="2.54" width="0.254" layer="94"/>
<wire x1="7.62" y1="2.54" x2="7.62" y2="0" width="0.254" layer="94"/>
<wire x1="7.62" y1="0" x2="7.62" y2="-2.54" width="0.254" layer="94"/>
<wire x1="7.62" y1="-2.54" x2="7.62" y2="-5.08" width="0.254" layer="94"/>
<wire x1="7.62" y1="-5.08" x2="-7.62" y2="-5.08" width="0.254" layer="94"/>
<wire x1="-7.62" y1="-5.08" x2="-7.62" y2="5.08" width="0.254" layer="94"/>
<wire x1="-7.62" y1="5.08" x2="7.62" y2="5.08" width="0.254" layer="94"/>
<text x="-7.63351875" y="5.85236875" size="1.781159375" layer="95">&gt;NAME</text>
<text x="-7.62108125" y="-7.62108125" size="1.77825" layer="96">&gt;VALUE</text>
<wire x1="7.62" y1="0" x2="5.08" y2="0" width="0.254" layer="94"/>
<wire x1="5.08" y1="0" x2="5.08" y2="-0.762" width="0.254" layer="94"/>
<pin name="1" x="10.16" y="2.54" visible="pad" length="short" direction="pas" rot="R180"/>
<pin name="2" x="10.16" y="-2.54" visible="pad" length="short" direction="pas" rot="R180"/>
<pin name="3" x="10.16" y="0" visible="pad" length="short" direction="pas" rot="R180"/>
</symbol>
</symbols>
<devicesets>
<deviceset name="MJ-3502N" prefix="J">
<description>3.5 mm, Mono, Right Angle, Through Hole, Audio Jack Connector </description>
<gates>
<gate name="G$1" symbol="MJ-3502N" x="0" y="0"/>
</gates>
<devices>
<device name="" package="CUI_MJ-3502N">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
<connect gate="G$1" pin="3" pad="3"/>
</connects>
<technologies>
<technology name="">
<attribute name="MANUFACTURER" value="CUI INC"/>
<attribute name="PART_REV" value="A"/>
<attribute name="STANDARD" value="MANUFACTURER RECOMMENDATIONS"/>
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
<part name="U1" library="microbuilder" deviceset="MAX4466" device="&quot;&quot;" value="MAX4466EXK+T"/>
<part name="FB1" library="microbuilder" deviceset="FERRITE" device="0805" value="FERRITE"/>
<part name="FB2" library="microbuilder" deviceset="FERRITE" device="0805" value="FERRITE"/>
<part name="R1" library="microbuilder" deviceset="RESISTOR" device="0805" value="1K"/>
<part name="R2" library="microbuilder" deviceset="RESISTOR" device="0805" value="1K"/>
<part name="C1" library="microbuilder" deviceset="CAP_CERAMIC" device="0805" value="0.1µF"/>
<part name="C2" library="microbuilder" deviceset="CAP_CERAMIC" device="0805" value="0.01uF"/>
<part name="U$2" library="microbuilder" deviceset="AGND" device=""/>
<part name="U$6" library="microbuilder" deviceset="AVCC" device=""/>
<part name="U$7" library="microbuilder" deviceset="GND" device=""/>
<part name="P+4" library="microbuilder" deviceset="VCC" device=""/>
<part name="U$3" library="microbuilder" deviceset="AVCC" device=""/>
<part name="U$4" library="microbuilder" deviceset="AVCC" device=""/>
<part name="U$8" library="microbuilder" deviceset="AGND" device=""/>
<part name="U$10" library="microbuilder" deviceset="AGND" device=""/>
<part name="R5" library="microbuilder" deviceset="RESISTOR" device="0805" value="1K"/>
<part name="U$12" library="microbuilder" deviceset="AGND" device=""/>
<part name="U$5" library="microbuilder" deviceset="AGND" device=""/>
<part name="R3" library="microbuilder" deviceset="RESISTOR" device="0805" value="1M"/>
<part name="R4" library="microbuilder" deviceset="RESISTOR" device="0805" value="1M"/>
<part name="U$9" library="microbuilder" deviceset="AGND" device=""/>
<part name="U$13" library="microbuilder" deviceset="AVCC" device=""/>
<part name="C3" library="microbuilder" deviceset="CAP_CERAMIC" device="0805" value="100pF"/>
<part name="VR1" library="microbuilder" deviceset="TRIMPOT" device="TC33X-2" value="TC33X-2-104E (100K)"/>
<part name="R7" library="microbuilder" deviceset="RESISTOR" device="0805" value="22K"/>
<part name="C4" library="microbuilder" deviceset="CAP_CERAMIC" device="0805" value="10uF"/>
<part name="MS1" library="adafruit" deviceset="FEATHERWING" device=""/>
<part name="GND1" library="supply1" library_urn="urn:adsk.eagle:library:371" deviceset="GND" device=""/>
<part name="P+1" library="supply1" library_urn="urn:adsk.eagle:library:371" deviceset="VCC" device=""/>
<part name="J1" library="MJ-3502N" deviceset="MJ-3502N" device=""/>
</parts>
<sheets>
<sheet>
<plain>
<text x="68.58" y="-5.08" size="1.778" layer="97">Gain =</text>
<text x="78.74" y="-2.54" size="1.778" layer="97">VR1+R7</text>
<text x="81.28" y="-7.62" size="1.778" layer="97">R5</text>
<wire x1="78.74" y1="-5.08" x2="88.9" y2="-5.08" width="0.1524" layer="97"/>
<text x="91.44" y="-5.08" size="1.778" layer="97">+1</text>
<text x="96.52" y="-5.08" size="1.778" layer="97">= ~25-125x gain</text>
<text x="12.7" y="33.02" size="1.778" layer="91">Low pass F3db = 1/R5*C4*2pi</text>
</plain>
<instances>
<instance part="U1" gate="G$1" x="93.98" y="55.88" smashed="yes">
<attribute name="NAME" x="83.82" y="73.66" size="1.27" layer="95"/>
<attribute name="VALUE" x="83.82" y="35.56" size="1.27" layer="96"/>
</instance>
<instance part="FB1" gate="G$1" x="93.98" y="88.9" smashed="yes">
<attribute name="NAME" x="92.71" y="90.805" size="1.27" layer="95"/>
<attribute name="VALUE" x="92.71" y="85.725" size="1.27" layer="95"/>
</instance>
<instance part="FB2" gate="G$1" x="93.98" y="99.06" smashed="yes">
<attribute name="NAME" x="92.71" y="100.965" size="1.27" layer="95"/>
<attribute name="VALUE" x="92.71" y="95.885" size="1.27" layer="95"/>
</instance>
<instance part="R1" gate="G$1" x="38.1" y="76.2" smashed="yes" rot="R90">
<attribute name="NAME" x="36.068" y="73.66" size="1.27" layer="95" font="vector" rot="R90"/>
<attribute name="VALUE" x="41.275" y="73.66" size="1.27" layer="96" font="vector" rot="R90"/>
</instance>
<instance part="R2" gate="G$1" x="38.1" y="91.44" smashed="yes" rot="R90">
<attribute name="NAME" x="36.068" y="88.9" size="1.27" layer="95" font="vector" rot="R90"/>
<attribute name="VALUE" x="41.275" y="88.9" size="1.27" layer="96" font="vector" rot="R90"/>
</instance>
<instance part="C1" gate="G$1" x="45.72" y="76.2" smashed="yes">
<attribute name="NAME" x="48.26" y="78.74" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="48.26" y="76.2" size="1.27" layer="96" font="vector"/>
</instance>
<instance part="C2" gate="G$1" x="53.34" y="58.42" smashed="yes" rot="R90">
<attribute name="NAME" x="50.8" y="60.96" size="1.27" layer="95" font="vector" rot="R90"/>
<attribute name="VALUE" x="53.34" y="60.96" size="1.27" layer="96" font="vector" rot="R90"/>
</instance>
<instance part="U$2" gate="G$1" x="99.06" y="83.82" smashed="yes">
<attribute name="VALUE" x="97.536" y="81.28" size="1.27" layer="96"/>
</instance>
<instance part="U$6" gate="G$1" x="88.9" y="104.14" smashed="yes">
<attribute name="VALUE" x="87.376" y="105.156" size="1.27" layer="96"/>
</instance>
<instance part="U$7" gate="G$1" x="88.9" y="83.82" smashed="yes">
<attribute name="VALUE" x="87.376" y="81.28" size="1.27" layer="96"/>
</instance>
<instance part="P+4" gate="VCC" x="99.06" y="104.14" smashed="yes">
<attribute name="VALUE" x="97.536" y="105.156" size="1.27" layer="96"/>
</instance>
<instance part="U$3" gate="G$1" x="78.74" y="68.58" smashed="yes">
<attribute name="VALUE" x="77.216" y="69.596" size="1.27" layer="96"/>
</instance>
<instance part="U$4" gate="G$1" x="38.1" y="101.6" smashed="yes">
<attribute name="VALUE" x="36.576" y="102.616" size="1.27" layer="96"/>
</instance>
<instance part="U$8" gate="G$1" x="78.74" y="43.18" smashed="yes">
<attribute name="VALUE" x="77.216" y="40.64" size="1.27" layer="96"/>
</instance>
<instance part="U$10" gate="G$1" x="45.72" y="68.58" smashed="yes">
<attribute name="VALUE" x="44.196" y="66.04" size="1.27" layer="96"/>
</instance>
<instance part="R5" gate="G$1" x="66.04" y="25.4" smashed="yes">
<attribute name="NAME" x="63.5" y="27.432" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="63.5" y="22.225" size="1.27" layer="96" font="vector"/>
</instance>
<instance part="U$12" gate="G$1" x="27.94" y="71.12" smashed="yes">
<attribute name="VALUE" x="26.416" y="68.58" size="1.27" layer="96"/>
</instance>
<instance part="U$5" gate="G$1" x="58.42" y="10.16" smashed="yes">
<attribute name="VALUE" x="56.896" y="7.62" size="1.27" layer="96"/>
</instance>
<instance part="R3" gate="G$1" x="60.96" y="50.8" smashed="yes" rot="R90">
<attribute name="NAME" x="58.928" y="48.26" size="1.27" layer="95" font="vector" rot="R90"/>
<attribute name="VALUE" x="64.135" y="48.26" size="1.27" layer="96" font="vector" rot="R90"/>
</instance>
<instance part="R4" gate="G$1" x="60.96" y="66.04" smashed="yes" rot="R90">
<attribute name="NAME" x="58.928" y="63.5" size="1.27" layer="95" font="vector" rot="R90"/>
<attribute name="VALUE" x="64.135" y="63.5" size="1.27" layer="96" font="vector" rot="R90"/>
</instance>
<instance part="U$9" gate="G$1" x="60.96" y="40.64" smashed="yes">
<attribute name="VALUE" x="59.436" y="38.1" size="1.27" layer="96"/>
</instance>
<instance part="U$13" gate="G$1" x="60.96" y="76.2" smashed="yes">
<attribute name="VALUE" x="59.436" y="77.216" size="1.27" layer="96"/>
</instance>
<instance part="C3" gate="G$1" x="91.44" y="12.7" smashed="yes" rot="R270">
<attribute name="NAME" x="93.98" y="10.16" size="1.27" layer="95" font="vector" rot="R270"/>
<attribute name="VALUE" x="91.44" y="10.16" size="1.27" layer="96" font="vector" rot="R270"/>
</instance>
<instance part="VR1" gate="G$1" x="93.98" y="25.4" smashed="yes" rot="MR270">
<attribute name="NAME" x="97.79" y="31.369" size="1.27" layer="95" rot="MR0"/>
<attribute name="VALUE" x="97.79" y="29.21" size="1.27" layer="96" rot="MR0"/>
</instance>
<instance part="R7" gate="G$1" x="81.28" y="25.4" smashed="yes">
<attribute name="NAME" x="78.74" y="27.432" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="78.74" y="22.225" size="1.27" layer="96" font="vector"/>
</instance>
<instance part="C4" gate="G$1" x="58.42" y="17.78" smashed="yes">
<attribute name="NAME" x="60.96" y="20.32" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="60.96" y="17.78" size="1.27" layer="96" font="vector"/>
</instance>
<instance part="MS1" gate="G$1" x="-2.54" y="-17.78" smashed="yes"/>
<instance part="GND1" gate="1" x="10.16" y="-30.48" smashed="yes">
<attribute name="VALUE" x="7.62" y="-33.02" size="1.778" layer="96"/>
</instance>
<instance part="P+1" gate="VCC" x="-5.08" y="-22.86" smashed="yes">
<attribute name="VALUE" x="-7.62" y="-25.4" size="1.778" layer="96" rot="R90"/>
</instance>
<instance part="J1" gate="G$1" x="7.62" y="71.12" smashed="yes">
<attribute name="NAME" x="-0.01351875" y="76.97236875" size="1.781159375" layer="95"/>
<attribute name="VALUE" x="-0.00108125" y="63.49891875" size="1.77825" layer="96"/>
</instance>
</instances>
<busses>
</busses>
<nets>
<net name="GND" class="0">
<segment>
<pinref part="U$7" gate="G$1" pin="GND"/>
<wire x1="88.9" y1="86.36" x2="88.9" y2="88.9" width="0.1524" layer="91"/>
<pinref part="FB1" gate="G$1" pin="P$1"/>
<wire x1="88.9" y1="88.9" x2="91.44" y2="88.9" width="0.1524" layer="91"/>
</segment>
<segment>
<pinref part="MS1" gate="G$1" pin="GND"/>
<pinref part="GND1" gate="1" pin="GND"/>
<wire x1="10.16" y1="-22.86" x2="10.16" y2="-27.94" width="0.1524" layer="91"/>
</segment>
</net>
<net name="VCC" class="0">
<segment>
<pinref part="P+4" gate="VCC" pin="VCC"/>
<wire x1="99.06" y1="101.6" x2="99.06" y2="99.06" width="0.1524" layer="91"/>
<pinref part="FB2" gate="G$1" pin="P$2"/>
<wire x1="99.06" y1="99.06" x2="96.52" y2="99.06" width="0.1524" layer="91"/>
</segment>
<segment>
<pinref part="MS1" gate="G$1" pin="3V"/>
<wire x1="5.08" y1="-22.86" x2="5.08" y2="-30.48" width="0.1524" layer="91"/>
<wire x1="5.08" y1="-30.48" x2="-5.08" y2="-30.48" width="0.1524" layer="91"/>
<pinref part="P+1" gate="VCC" pin="VCC"/>
<wire x1="-5.08" y1="-30.48" x2="-5.08" y2="-25.4" width="0.1524" layer="91"/>
<pinref part="MS1" gate="G$1" pin="AREF"/>
<wire x1="7.62" y1="-22.86" x2="5.08" y2="-22.86" width="0.1524" layer="91"/>
<junction x="5.08" y="-22.86"/>
</segment>
</net>
<net name="N$3" class="0">
<segment>
<pinref part="R1" gate="G$1" pin="1"/>
<wire x1="38.1" y1="58.42" x2="35.56" y2="58.42" width="0.1524" layer="91"/>
<wire x1="38.1" y1="71.12" x2="38.1" y2="58.42" width="0.1524" layer="91"/>
<pinref part="C2" gate="G$1" pin="P$1"/>
<wire x1="48.26" y1="58.42" x2="38.1" y2="58.42" width="0.1524" layer="91"/>
<junction x="38.1" y="58.42"/>
<pinref part="J1" gate="G$1" pin="2"/>
<wire x1="17.78" y1="68.58" x2="17.78" y2="58.42" width="0.1524" layer="91"/>
<wire x1="17.78" y1="58.42" x2="38.1" y2="58.42" width="0.1524" layer="91"/>
</segment>
</net>
<net name="N$4" class="0">
<segment>
<pinref part="R2" gate="G$1" pin="1"/>
<pinref part="R1" gate="G$1" pin="2"/>
<wire x1="38.1" y1="86.36" x2="38.1" y2="83.82" width="0.1524" layer="91"/>
<pinref part="C1" gate="G$1" pin="P$1"/>
<wire x1="38.1" y1="83.82" x2="38.1" y2="81.28" width="0.1524" layer="91"/>
<wire x1="38.1" y1="83.82" x2="45.72" y2="83.82" width="0.1524" layer="91"/>
<wire x1="45.72" y1="83.82" x2="45.72" y2="81.28" width="0.1524" layer="91"/>
<junction x="38.1" y="83.82"/>
</segment>
</net>
<net name="N$5" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="IN+"/>
<pinref part="C2" gate="G$1" pin="P$2"/>
<wire x1="81.28" y1="58.42" x2="60.96" y2="58.42" width="0.1524" layer="91"/>
<pinref part="R3" gate="G$1" pin="2"/>
<wire x1="60.96" y1="58.42" x2="55.88" y2="58.42" width="0.1524" layer="91"/>
<wire x1="60.96" y1="58.42" x2="60.96" y2="55.88" width="0.1524" layer="91"/>
<junction x="60.96" y="58.42"/>
<pinref part="R4" gate="G$1" pin="1"/>
<wire x1="60.96" y1="60.96" x2="60.96" y2="58.42" width="0.1524" layer="91"/>
</segment>
</net>
<net name="AVCC" class="0">
<segment>
<pinref part="U$6" gate="G$1" pin="AVCC"/>
<wire x1="88.9" y1="101.6" x2="88.9" y2="99.06" width="0.1524" layer="91"/>
<pinref part="FB2" gate="G$1" pin="P$1"/>
<wire x1="88.9" y1="99.06" x2="91.44" y2="99.06" width="0.1524" layer="91"/>
</segment>
<segment>
<pinref part="U1" gate="G$1" pin="VCC"/>
<pinref part="U$3" gate="G$1" pin="AVCC"/>
<wire x1="81.28" y1="63.5" x2="78.74" y2="63.5" width="0.1524" layer="91"/>
<wire x1="78.74" y1="63.5" x2="78.74" y2="66.04" width="0.1524" layer="91"/>
</segment>
<segment>
<pinref part="R2" gate="G$1" pin="2"/>
<pinref part="U$4" gate="G$1" pin="AVCC"/>
<wire x1="38.1" y1="96.52" x2="38.1" y2="99.06" width="0.1524" layer="91"/>
</segment>
<segment>
<pinref part="U$13" gate="G$1" pin="AVCC"/>
<pinref part="R4" gate="G$1" pin="2"/>
<wire x1="60.96" y1="73.66" x2="60.96" y2="71.12" width="0.1524" layer="91"/>
</segment>
</net>
<net name="AGND" class="0">
<segment>
<pinref part="FB1" gate="G$1" pin="P$2"/>
<pinref part="U$2" gate="G$1" pin="AGND"/>
<wire x1="96.52" y1="88.9" x2="99.06" y2="88.9" width="0.1524" layer="91"/>
<wire x1="99.06" y1="88.9" x2="99.06" y2="86.36" width="0.1524" layer="91"/>
</segment>
<segment>
<pinref part="C1" gate="G$1" pin="P$2"/>
<pinref part="U$10" gate="G$1" pin="AGND"/>
<wire x1="45.72" y1="73.66" x2="45.72" y2="71.12" width="0.1524" layer="91"/>
</segment>
<segment>
<pinref part="U1" gate="G$1" pin="GND"/>
<pinref part="U$8" gate="G$1" pin="AGND"/>
<wire x1="81.28" y1="48.26" x2="78.74" y2="48.26" width="0.1524" layer="91"/>
<wire x1="78.74" y1="48.26" x2="78.74" y2="45.72" width="0.1524" layer="91"/>
</segment>
<segment>
<pinref part="R3" gate="G$1" pin="1"/>
<pinref part="U$9" gate="G$1" pin="AGND"/>
<wire x1="60.96" y1="45.72" x2="60.96" y2="43.18" width="0.1524" layer="91"/>
</segment>
<segment>
<pinref part="C4" gate="G$1" pin="P$2"/>
<pinref part="U$5" gate="G$1" pin="AGND"/>
<wire x1="58.42" y1="15.24" x2="58.42" y2="12.7" width="0.1524" layer="91"/>
</segment>
<segment>
<pinref part="U$12" gate="G$1" pin="AGND"/>
<pinref part="J1" gate="G$1" pin="1"/>
<wire x1="27.94" y1="73.66" x2="17.78" y2="73.66" width="0.1524" layer="91"/>
</segment>
</net>
<net name="N$6" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="OUT"/>
<wire x1="111.76" y1="55.88" x2="106.68" y2="55.88" width="0.1524" layer="91"/>
<wire x1="111.76" y1="17.78" x2="111.76" y2="25.4" width="0.1524" layer="91"/>
<pinref part="VR1" gate="G$1" pin="S"/>
<wire x1="111.76" y1="25.4" x2="111.76" y2="40.64" width="0.1524" layer="91"/>
<wire x1="111.76" y1="40.64" x2="111.76" y2="55.88" width="0.1524" layer="91"/>
<wire x1="93.98" y1="20.32" x2="93.98" y2="17.78" width="0.1524" layer="91"/>
<wire x1="93.98" y1="17.78" x2="111.76" y2="17.78" width="0.1524" layer="91"/>
<pinref part="C3" gate="G$1" pin="P$1"/>
<wire x1="96.52" y1="12.7" x2="111.76" y2="12.7" width="0.1524" layer="91"/>
<wire x1="111.76" y1="12.7" x2="111.76" y2="17.78" width="0.1524" layer="91"/>
<junction x="111.76" y="17.78"/>
<pinref part="VR1" gate="G$1" pin="A"/>
<wire x1="99.06" y1="25.4" x2="111.76" y2="25.4" width="0.1524" layer="91"/>
<junction x="111.76" y="25.4"/>
<pinref part="MS1" gate="G$1" pin="GPIOA1"/>
<wire x1="15.24" y1="-22.86" x2="15.24" y2="-27.94" width="0.1524" layer="91"/>
<wire x1="15.24" y1="-27.94" x2="134.62" y2="-27.94" width="0.1524" layer="91"/>
<wire x1="134.62" y1="-27.94" x2="134.62" y2="40.64" width="0.1524" layer="91"/>
<wire x1="134.62" y1="40.64" x2="111.76" y2="40.64" width="0.1524" layer="91"/>
<junction x="111.76" y="40.64"/>
</segment>
</net>
<net name="N$1" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="IN-"/>
<wire x1="81.28" y1="53.34" x2="73.66" y2="53.34" width="0.1524" layer="91"/>
<wire x1="73.66" y1="53.34" x2="73.66" y2="25.4" width="0.1524" layer="91"/>
<pinref part="R5" gate="G$1" pin="2"/>
<wire x1="71.12" y1="25.4" x2="73.66" y2="25.4" width="0.1524" layer="91"/>
<pinref part="R7" gate="G$1" pin="1"/>
<wire x1="73.66" y1="25.4" x2="76.2" y2="25.4" width="0.1524" layer="91"/>
<junction x="73.66" y="25.4"/>
<wire x1="73.66" y1="25.4" x2="73.66" y2="12.7" width="0.1524" layer="91"/>
<pinref part="C3" gate="G$1" pin="P$2"/>
<wire x1="73.66" y1="12.7" x2="88.9" y2="12.7" width="0.1524" layer="91"/>
</segment>
</net>
<net name="N$7" class="0">
<segment>
<pinref part="R5" gate="G$1" pin="1"/>
<wire x1="60.96" y1="25.4" x2="58.42" y2="25.4" width="0.1524" layer="91"/>
<pinref part="C4" gate="G$1" pin="P$1"/>
<wire x1="58.42" y1="25.4" x2="58.42" y2="22.86" width="0.1524" layer="91"/>
</segment>
</net>
<net name="N$2" class="0">
<segment>
<pinref part="R7" gate="G$1" pin="2"/>
<pinref part="VR1" gate="G$1" pin="E"/>
<wire x1="86.36" y1="25.4" x2="88.9" y2="25.4" width="0.1524" layer="91"/>
</segment>
</net>
</nets>
</sheet>
</sheets>
</schematic>
</drawing>
<compatibility>
<note version="8.2" severity="warning">
Since Version 8.2, EAGLE supports online libraries. The ids
of those online libraries will not be understood (or retained)
with this version.
</note>
<note version="8.3" severity="warning">
Since Version 8.3, EAGLE supports URNs for individual library
assets (packages, symbols, and devices). The URNs of those assets
will not be understood (or retained) with this version.
</note>
</compatibility>
</eagle>
