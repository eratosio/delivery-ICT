import json
import math
from senaps_sensor.parsers import PandasObservationParser
from senaps_sensor.models import UnivariateResult, Observation
from datetime import datetime
from as_models.models import model
from constant import ORG_ID

@model(f"eratos.sandbox.calculate_sap_flow_{ORG_ID}")
def create_workflow(context):
    # extract ports (see manifest.json)

    settings = getattr(context.ports, 'settings', None)

    if settings and settings.value:
        json_settings = json.loads(settings.value)
    else:
        json_settings = {}

    # Get the platform ID that this workflow will run for
    platform_ids = json_settings.get('platform', [])

    if isinstance(platform_ids, str):
        platform_ids = [platform_ids]

    for platform_id in platform_ids:
        platform = context.sensor_client.get_platform(id=platform_id)
        # Standard Physical Probe Installation Protocol
        circumference = 0.6283  # metres, a 10cm radius or 20cm diameter Tree Standard.
        wc = 1.7283
        bark_thickness = 0.0050  # metres, changed number 04/09/2024 by ICT to 5mm.
        sapwood_depth = 0.0420  # metres, 4.2cm depth.
        probe_length = 0.035  # metres, 3.5cm long probe needle.
        probe_depths = [0.0075, 0.0225]  # first number in array is "0" reference, 2nd is "1".
        # 0 reference in array = outer thermistor position within the sapwood measured, starting point is the
        # transition from bark to sapwood.
        # 1 reference in array = inner thermistor position within the sapwood measured, starting point is the
        # transition from bark to sapwood.
        fsv = 0.64347
        offset_inner = 0
        offset_outer = 0
        probe_edge = 0.030  # metres
        # "linear_decay" or "inner_velocity"
        rem_type = "linear_decay"
        metadata = False  # medadata is false / zero / 0

        # Get the metadata for the Platform - this will be used for the Sap FLow Calculations
        if platform.usermetadata is None:  # if metadata is defined as 0 in senaps for the device, run this:
            print(f"No metadata found for {platform_id} - using defaults")

            circumference = 0.6283  # metres, a 10cm radius or 20cm diameter Tree Standard.
            wc = 1.7283
            bark_thickness = 0.0050  # metres
            sapwood_depth = 0.0420  # metres
            probe_length = 0.035  # metres
            probe_depths = [0.0075, 0.0225]  # first number in array is "0" reference, 2nd is "1".
            # 0 reference in array = outer thermistor position within the sapwood measured, starting point is the
            # transition from bark to sapwood.
            # 1 reference in array = inner thermistor position within the sapwood measured, starting point is the
            # transition from bark to sapwood.
            fsv = 0.64347
            offset_inner = 0  # cm/hr
            offset_outer = 0  # cm/hr
            probe_edge = 0.030  # metres
            # "linear_decay" or "inner_velocity"
            rem_type = "linear_decay"
        else:  # else the meta does exist = 1, then fill the varibles with the metadata elements:
            print(f"Using Metadata for {platform_id}")
            metadata = True  # Meta data is True thus = 1
            if "properties" not in platform.usermetadata:
                if "circumference" in platform.usermetadata:
                    circumference = platform.usermetadata["circumference"]
                if "wc" in platform.usermetadata:
                    wc = platform.usermetadata["wc"]
                if "bark_thickness" in platform.usermetadata:
                    bark_thickness = platform.usermetadata["bark_thickness"]
                if "sapwood_depth" in platform.usermetadata:
                    sapwood_depth = platform.usermetadata["sapwood_depth"]
                if "probe_length" in platform.usermetadata:
                    probe_length = platform.usermetadata["probe_length"]
                if "probe_depths" in platform.usermetadata:
                    probe_depths = platform.usermetadata["probe_depths"]
                if "fsv" in platform.usermetadata:
                    fsv = platform.usermetadata["fsv"]
                if "offset_inner" in platform.usermetadata:
                    offset_inner = platform.usermetadata["offset_inner"]
                if "offset_outer" in platform.usermetadata:
                    offset_outer = platform.usermetadata["offset_outer"]

                if "probe_edge" in platform.usermetadata:
                    probe_edge = platform.usermetadata["probe_edge"]
                if "rem_type" in platform.usermetadata:
                    rem_type = platform.usermetadata["rem_type"]
            else:
                if "circumference" in platform.usermetadata["properties"]:
                    circumference = platform.usermetadata["properties"]["circumference"]

                if "wc" in platform.usermetadata["properties"]:
                    wc = platform.usermetadata["properties"]["wc"]

                if "bark-thickness" in platform.usermetadata["properties"]:
                    bark_thickness = platform.usermetadata["properties"]["bark-thickness"]

                if "sapwood-depth" in platform.usermetadata["properties"]:
                    sapwood_depth = platform.usermetadata["properties"]["sapwood-depth"]

                if "probe-length" in platform.usermetadata["properties"]:
                    probe_length = platform.usermetadata["properties"]["probe-length"]

                if "probe-depths" in platform.usermetadata["properties"]:
                    probe_depths = platform.usermetadata["properties"]["probe-depths"]

                if "fsv" in platform.usermetadata["properties"]:
                    fsv = platform.usermetadata["properties"]["fsv"]

                if "offset_inner" in platform.usermetadata["properties"]:
                    offset_inner = platform.usermetadata["properties"]["offset_inner"]

                if "offset_outer" in platform.usermetadata["properties"]:
                    offset_outer = platform.usermetadata["properties"]["offset_outer"]

                if "probe_edge" in platform.usermetadata["properties"]:
                    probe_edge = platform.usermetadata["properties"]["probe_edge"]

                if "rem_type" in platform.usermetadata["properties"]:
                    rem_type = platform.usermetadata["properties"]["rem_type"]

        # print(f"Circumference: {circumference}")
        # print(f"bark_thickness: {bark_thickness}")
        # print(f"sapwood_depth: {sapwood_depth}")
        # print(f"probe_length: {probe_length}")
        # print(f"probe_depths: {probe_depths}")
        # print(f"FSV: {fsv}")

        #######################################################################

        # # Sap Velocity Constants
        # cw = 1200               # Heat Capacity of Wood(kJ)
        # cs = 4182               # Heat Capacity of Sap(Water)(kJ)
        # ps = 1                  # Density of water (g/cm3)

        # # Wood properties for sap flow calculations, found by taking cores sample(or estimation)
        # fw = 1.0                # Sapwood Fresh Weight(g)
        # dw = 0.5                # Sapwood Dry Weight(g)
        # fv = 1                  # Sapwood Dry Volume(cm3)

        # mc = (fw - dw) / dw     # Water Content (As decimal)
        # pb = dw / fv            # Density of Sapwood(DryWeight/GreenVolume)(g/cm3)

        # Sap Velocity Factor
        # Fsv = (pb * (cw + (mc * cs))) / (ps * cs)
        # We are not calculating Fsv here - we are getting this from the Platform Metadata

        # Taking these values for Sap Flow Meter probes and the size of the tree
        probe_edge = probe_edge * 100  # Converts meta data metres into cm.
        # e.g. 3.0cm

        probe_length = probe_length * 100  # Converts meta data metres into cm.
        # Probe length, in cm
        # e.g. 3.5cm

        # Reference below might be wrong noted by ICT 04/09/2024
        # probe_depths = [0.75, 2.25] # Probe thermistor depths from tip???, in cm
        # probe_depth1 = probe_length - (probe_depths[1] * 100) # Depth of Probes first thermistor(outer), in cm      # 3.5cm - 2.25cm = 1.25cm
        # probe_depth2 = probe_length - (probe_depths[0] * 100) # Depth of Probes second thermistor(inner), in cm     # 3.5cm - 0.75cm = 2.75cm

        # Reference:
        # probe_depths = [0.0075, 0.0225] # first number in array is "0" reference, 2nd is "1".
        # 0 reference in array = outer thermistor position within the sapwood measured, starting point is the
        # transition from bark to sapwood.
        # 1 reference in array = inner thermistor position within the sapwood measured, starting point is the
        # transition from bark to sapwood.

        # probe_length = 0.035 # metres, 3.5cm long probe needle.

        if metadata:  # If metadata variable is switched to true "1" from metadata file containing true metadata:
            probe_depth1 = probe_depths[0] * 100  # New variable, Probe depths are metres in metadata * 100 = cm. e.g.
            # 0.0075m in from bark, outer measurement point
            # 0.0075 * 100 = 0.75cm
            probe_depth2 = probe_depths[1] * 100  # New variable, Probe depths are metres in metadata * 100 = cm. e.g
            # 0.0225m in from bark, inner measurement point
            # 0.0225 * 100 = 2.25cm


        else:  # if metadata variable is not switched to true, define these aka False Metadata = 0:, will assume position of the thermistors as probe depths (referencing the base of the needle as the surface of the xylem)
            probe_depth1 = probe_length - (
                        probe_depths[1] * 100)  # New variable, Depth of Probes first thermistor(outer), in cm.
            # 3.5cm - (0.0225 * 100) = 1.25cm
            #
            probe_depth2 = probe_length - (
                        probe_depths[0] * 100)  # New variable, Depth of Probes second thermistor(inner), in cm.
            # 3.5cm - (0.0075 * 100) = 2.75cm

        bark_thickness = bark_thickness * 100  # Bark Thickness, in cm
        sapwood_depth = sapwood_depth * 100  # Sapwood Depth, in cm
        trunk_circumference = circumference * 100  # Trunk Circumference(including bark), in cm
        # 62.83cm = 0.6283m * 100
        trunk_diameter = trunk_circumference / math.pi  # Trunk Diameter(including bark), in cm
        # = 62.83 / pi = 19.999410 cm

        # Calculate width of annuli depending on probe depths
        print('\n')
        print('Converted values:')
        print(f"probe_edge: {probe_edge}")
        print(f"sapwood_depth: {sapwood_depth}")
        print(f"probe_depth2: {probe_depth2}")

        # Equation for inner and outer annulus and remainder in the event that
        # the probe edge is larger than the sapwood depth & the probe depth2
        # is less than the sapwood depth.
        # the following 3 'if' statements set conditions in the calculation of the sapwood annulus width based on sapwood depth and placement of thermistors
        if probe_edge >= sapwood_depth and probe_depth2 < sapwood_depth:  # sapwood depth is
            print('2')
            outer_annulus_width = probe_depth1 + 0.0075 * 100  # Convert to cm
            inner_annulus_width = sapwood_depth - outer_annulus_width
            inner_sapwood_annulus = (math.pow(((trunk_diameter / 2) - (bark_thickness + outer_annulus_width)),
                                              2) * math.pi) - \
                                    (math.pow(((trunk_diameter / 2) - (
                                                bark_thickness + outer_annulus_width + inner_annulus_width)),
                                              2) * math.pi)

            rem_sapwood_annulus = 0

            # If probe depth2 inner is in Heartwood or Air then report zero's
        # Where the calculation can't complete.
        if probe_depth2 > sapwood_depth:  # depth2 = inner thermistor depth into the sapwood layer.
            # exampe: if 2.25cm > 4.2cm do this:
            print('1')
            outer_annulus_width = sapwood_depth
            inner_sapwood_annulus = 0
            rem_sapwood_annulus = 0

        if sapwood_depth > probe_edge:
            print('3')
            # 4.2cm > 3.0cm is true do this:
            outer_annulus_width = probe_depth1 + 0.0075 * 100  # Convert to cm
            # 1.5cm = 0.75cm + 0.0075*100
            inner_annulus_width = 0.015 * 100  # Convert to cm
            # 1.5cm for inner_annulus_width
            print("outer_annulus_width", outer_annulus_width)
            print("inner_annulus_width", inner_annulus_width)
            rem_annulus_width = sapwood_depth - (outer_annulus_width + inner_annulus_width)
            # 1.2cm = 4.2 - (1.5 + 1.5) Confirmed 17/09/2024 ok.
            print("rem_annulus_width", rem_annulus_width)

            # Annulus area calculations (comment added 18/09; changed order to outer_sapwood_annulus then inner_sapwood_annulus then rem_sapwood_annulus -- BU)

            outer_sapwood_annulus = (math.pow(((trunk_diameter / 2) - bark_thickness), 2) * math.pi) - \
                                    (math.pow(((trunk_diameter / 2) - (bark_thickness + outer_annulus_width)),
                                              2) * math.pi)
            # Surface of the Outer Sapwood Annulus in cm^2
            # ((19.999410/2) - (0.5))^2 x pi
            # 9.5 ^ 2 * pi
            # 283.528737
            # -
            # ((19.999410/2) - (0.5 + 1.5))^2 x pi
            # 8 ^ 2 * pi
            # 201.0619298
            # 283.528737 - 201.0619298
            # 82.49981

            inner_sapwood_annulus = (math.pow(((trunk_diameter / 2) - (bark_thickness + outer_annulus_width)),
                                              2) * math.pi) - \
                                    (math.pow(((trunk_diameter / 2) - (
                                                bark_thickness + outer_annulus_width + inner_annulus_width)),
                                              2) * math.pi)
            # Surface of the Inner Sapwood Annulus in cm^2
            # ((19.999410/2) - (0.5 + 1.5))^2 x pi
            # (10 - (2.0))^2 x 3.14
            # 8^2 x pi
            # 201.061929
            #     -
            # ((19.999410/2) - (0.5 + 1.5 + 1.5))^2 x math.pi
            # (10 - (3.5))^2 x 3.14
            # 6.5^2 x 3.14
            # 132.73229cm^2
            # 201.061929 - 132.73229 =
            # 68.329639cm^2

            rem_sapwood_annulus = (math.pow(
                ((trunk_diameter / 2) - (bark_thickness + outer_annulus_width + inner_annulus_width)), 2) * math.pi) - \
                                  (math.pow(((trunk_diameter / 2) - (bark_thickness + sapwood_depth)), 2) * math.pi)
            # Surface of the Remainder Sapwood Annulus in cm^2
            # ((19.999410/2) - (0.5 + 1.5 + 1.5))^2 x pi
            # (10 - 3.5)^2 * 3.14
            # 132.73228
            # -
            #  ((19.999410/2) - (0.5 + 4.2))^2 x pi
            # 88.24734 (also the heartwood area)
            # 132.73228 - 88.24734 =
            # 44.48494cm^2

            # To check out these calculations, the area of the stem without the bark was matched with the sum of the annulus areas (heartwood, remainder, inner, outer)
            # area of stem (less bark) = circumference/2 ^2 * pi
            # 19.999/2 - 0.5 ^2 * pi = 283.5287
            # sum of annulus areas =  88.24734 + 44.4849 + 68.32963 + 82.4998 = 283.52

        latest_obs = context.sensor_client.get_observations(streamid=f'{platform_id}.cumulative-sap-flow', limit=1,
                                                            sort='descending', media="csv",
                                                            parser=PandasObservationParser())
        # print(latest_obs.size)
        print(f"Latest Obs - Size: {latest_obs.size}")

        if latest_obs.size == 1:
            # print("Latest %s observation found at: %s" % ({platform_id}.corrected-outer, latest_obs.index[-1]))
            # only upload the most recent data by starting at the latest observation
            start = latest_obs.index[-1].isoformat()
            cumulative_sap_flow_total = latest_obs[f"{platform_id}.cumulative-sap-flow"].values[0]
            print(f"Start: {start}")
            print(f"Cumulative Sap Flow: {cumulative_sap_flow_total}")

        elif latest_obs.size == 0:
            start = datetime(1900, 1, 1).isoformat()
            cumulative_sap_flow_total = 0
            print(f"Start: {start}")
            print(f"Cumulative Sap Flow: {cumulative_sap_flow_total}")

        # --- Extract unCorrected - Outer and Inner Sap Flow Data ---#

        df = context.sensor_client.get_observations(
            streamid=f'{platform_id}.uncorrected-outer,{platform_id}.uncorrected-inner',
            start=start,
            limit=200000,
            limitstreams=20,
            media="csv",
            sort="ascending",
            parser=PandasObservationParser(),
            platformid=platform_id)

        # Setup arrays that will hold results to be output to streams
        # ICT added uncorrected inner and outer here so that we can process offsets to streams.
        # calculated_uncorrected_outer = []
        # calculated_uncorrected_inner = []

        calculated_uncorrected_outer_offset = []
        calculated_uncorrected_inner_offset = []

        calculated_corrected_outer = []  # WC corrected Heat pulse Velocity
        calculated_corrected_inner = []  # WC corrected Heat pulse Velocity

        calculated_sap_velocity_outer = []  # Fsv corrected Sap Velocity
        calculated_sap_velocity_inner = []  # Fsv corrected Sap Velocity

        calculated_outer_sapflow = []
        calculated_inner_sapflow = []

        calculated_remainder_sapflow = []

        cumulative_sap_flow = []

        observation_count = 0

        # Loop through Dataframe and Calculate Sap Flow
        for ts, row in df.iterrows():

            if (start == ts.isoformat()):
                print("Skipping first result, as this has already been processed")
                continue

            observation_count = observation_count + 1

            # ICT Added offset application to this section
            Vh_outer = row[
                           f"{platform_id}.uncorrected-outer"] + offset_outer  # Uncorrected Heatpulse Velocities + offset
            Vh_inner = row[
                           f"{platform_id}.uncorrected-inner"] + offset_inner  # Uncorrected Heatpulse Velocities + offset

            # Multiply by wc to corrected
            # Corrected Outer Heatpulse Velocity
            Vc_outer = Vh_outer * wc  # ( * fsv)
            # fsv removed here 04/09/2024 by ICT as Vc_outer is simple mulptiplying Vh_outer * wc only.

            # Corrected Inner Heatpulse Velocity
            Vc_inner = Vh_inner * wc  # (* fsv)
            # fsv removed here 04/09/2024 by ICT as Vc_outer is simple mulptiplying Vh_inner * wc only.

            if (math.isnan(Vc_outer) or math.isnan(Vc_inner)):
                print(
                    f"Skipping as there is missing data and we can't calculate SAP Flow: {ts.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}")
                continue

            # Sap Velocities, in cm/hr
            Vs_outer = (Vc_outer * fsv)  # ( + offset_outer)
            # offset application here is incorrect, this should be done at Vh_outer stage.
            # Noted by ICT 04/09/2024.
            Vs_inner = (Vc_inner * fsv)  # ( + offset_inner)
            # offset application here is incorrect, this should be done at Vh_inner stage.
            # Noted by ICT 04/09/2024.

            # Sap Flow of each annulus, in kg/hr
            outer_sapflow = (Vs_outer * outer_sapwood_annulus) / 1000  # converts cm/hr to kg/hr
            inner_sapflow = (Vs_inner * inner_sapwood_annulus) / 1000  # converts cm/hr to kg/hr
            rem_sapflow = 0

            # Calculate Remainder Sap Flow
            if rem_type == "linear_decay":
                rem_sapflow = (Vs_inner / 2 * rem_sapwood_annulus) / 1000
            elif rem_type == "inner_velocity":
                rem_sapflow = (Vs_inner * rem_sapwood_annulus) / 1000

            # Total Sap Flow, in kg/hr
            total_sapflow = outer_sapflow + inner_sapflow + rem_sapflow

            # Keep a running total of cumulative Total Sap Flow
            cumulative_sap_flow_total += total_sapflow

            print(f"Current time value: {ts.strftime('%Y-%m-%dT%H:%M:%S.%fZ')} - Values: {Vs_outer}, {Vc_inner}")

            # Add data to output arrays
            calculated_uncorrected_outer_offset.append(
                UnivariateResult(t=ts.strftime('%Y-%m-%dT%H:%M:%S.%fZ'), v=Vh_outer))
            # changed uncorrected_outer to being the offset version that gets created in senaps.
            calculated_uncorrected_inner_offset.append(
                UnivariateResult(t=ts.strftime('%Y-%m-%dT%H:%M:%S.%fZ'), v=Vh_inner))
            # changed uncorrected_inner to being the offset version that gets created in senaps.

            # These are the corrected heatpulse velocity for WC
            calculated_corrected_outer.append(UnivariateResult(t=ts.strftime('%Y-%m-%dT%H:%M:%S.%fZ'), v=Vc_outer))
            calculated_corrected_inner.append(UnivariateResult(t=ts.strftime('%Y-%m-%dT%H:%M:%S.%fZ'), v=Vc_inner))

            # Added sap velocity values here (these are the Fsv corrected values
            calculated_sap_velocity_outer.append(UnivariateResult(t=ts.strftime('%Y-%m-%dT%H:%M:%S.%fZ'), v=Vs_outer))
            calculated_sap_velocity_inner.append(UnivariateResult(t=ts.strftime('%Y-%m-%dT%H:%M:%S.%fZ'), v=Vs_inner))

            calculated_outer_sapflow.append(UnivariateResult(t=ts.strftime('%Y-%m-%dT%H:%M:%S.%fZ'), v=outer_sapflow))
            calculated_inner_sapflow.append(UnivariateResult(t=ts.strftime('%Y-%m-%dT%H:%M:%S.%fZ'), v=inner_sapflow))

            calculated_remainder_sapflow.append(UnivariateResult(t=ts.strftime('%Y-%m-%dT%H:%M:%S.%fZ'), v=rem_sapflow))
            cumulative_sap_flow.append(
                UnivariateResult(t=ts.strftime('%Y-%m-%dT%H:%M:%S.%fZ'), v=cumulative_sap_flow_total))

        print(f"Observations processed: {observation_count}")

        # Added outputs for sending uncorrected-inner-offset and outer-offset to senaps.
        output = Observation()
        output.results = calculated_uncorrected_inner_offset

        context.sensor_client.create_observations(output, streamid=f"{platform_id}.uncorrected-inner-offset")

        # Added outputs for sending uncorrected-inner-offset and outer-offset to senaps.
        output = Observation()
        output.results = calculated_uncorrected_outer_offset

        context.sensor_client.create_observations(output, streamid=f"{platform_id}.uncorrected-outer-offset")

        output = Observation()
        output.results = calculated_corrected_inner

        context.sensor_client.create_observations(output, streamid=f"{platform_id}.corrected-inner")

        output = Observation()
        output.results = calculated_corrected_outer

        context.sensor_client.create_observations(output, streamid=f"{platform_id}.corrected-outer")

        # Added Sap Velocities for inner and outer which are Fsv
        output = Observation()
        output.results = calculated_sap_velocity_inner

        context.sensor_client.create_observations(output, streamid=f"{platform_id}.sap-velocity-inner")

        # Added Sap Velocities for inner and outer which are Fsv
        output = Observation()
        output.results = calculated_sap_velocity_outer

        context.sensor_client.create_observations(output, streamid=f"{platform_id}.sap-velocity-outer")

        output = Observation()
        output.results = calculated_outer_sapflow

        context.sensor_client.create_observations(output, streamid=f"{platform_id}.calculated-sap-flow-outer")

        output = Observation()
        output.results = calculated_inner_sapflow

        context.sensor_client.create_observations(output, streamid=f"{platform_id}.calculated-sap-flow-inner")

        output = Observation()
        output.results = calculated_remainder_sapflow

        context.sensor_client.create_observations(output, streamid=f"{platform_id}.calculated-sap-flow-remainder")

        output = Observation()
        output.results = cumulative_sap_flow

        context.sensor_client.create_observations(output, streamid=f"{platform_id}.cumulative-sap-flow")