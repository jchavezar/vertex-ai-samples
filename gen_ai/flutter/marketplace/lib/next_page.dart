import 'package:flutter/material.dart';

class NextPage extends StatefulWidget {
  final String ? imageGcsUri;
  final String ? sensorLensMount;
  final String ? sensorType;
  final String ? sensorResolution;
  final String ? sensorImageStabilization;
  final String ? sensorVideoCapabilities;
  final String ? contShootSpeed;
  final String ? autofocusSystem;
  final String ? isoRange;
  final String ? connectivity;
  final String ? gemMetadataText;
  final String ? summary;

  const NextPage({
    super.key,
    this.imageGcsUri,
    this.sensorLensMount,
    this.sensorType,
    this.sensorResolution,
    this.sensorImageStabilization,
    this.sensorVideoCapabilities,
    this.contShootSpeed,
    this.autofocusSystem,
    this.isoRange,
    this.connectivity,
    this.gemMetadataText,
    this.summary,
  });
  @override
  State<NextPage> createState() => _NextPageState();
}

class _NextPageState extends State<NextPage> {

  @override
  Widget build(BuildContext context) {
    double windowSize = MediaQuery.of(context).size.width;
    return Scaffold(
      body: ListView(
        scrollDirection: Axis.vertical,
        children: [
          Container(
              padding: const EdgeInsets.only(left: 70.0, right: 5.0, top: 25.0,),
              height: 100,
              child: Row(
                children: [
                  const Center(
                    child: Text(
                      "Photos Listing and Metadata Powered by: ",
                      style: TextStyle(fontSize: 24.0, fontWeight: FontWeight.bold),
                    ),
                  ),
                  Padding(
                      padding: const EdgeInsets.all(2.0),
                      child: Image.network("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Google_Gemini_logo.svg/2560px-Google_Gemini_logo.svg.png")),
                ],
              )
          ),
          const SizedBox(height: 20.0),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              Container(
                  padding: const EdgeInsets.all(12.0),
                  margin: const EdgeInsets.only(top: 15.0, right: 8.0, left: 8.0,),
                  height: windowSize*0.40,
                  width: windowSize*0.8*0.50,
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Container(
                            decoration: const BoxDecoration(
                                borderRadius: BorderRadius.all(Radius.circular(12.0)),
                              color: Colors.black,
                            ),
                            child: ClipRRect(
                              borderRadius: const BorderRadius.all(Radius.circular(11.0)),
                              child: Image.network("${widget.imageGcsUri}",
                                  fit: BoxFit.fill
                              ),
                            ),
                          )
                    ],
                  )
              ),
              Container(
                width: windowSize*0.8*0.60,
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(12.0),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.grey.withOpacity(0.5), // Shadow color
                      spreadRadius: 2, // How much the shadow spreads
                      blurRadius: 5, // How blurry the shadow is
                      offset: const Offset(0, 3), // Shadow offset (vertical in this case)
                    ),
                  ],
                ),
                padding: const EdgeInsets.all(12.0),
                margin: const EdgeInsets.only(top: 15.0, right: 30.0),
                // height: windowSize*0.32,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text("Description", style: TextStyle(fontSize: 20.0, fontWeight: FontWeight.bold),),
                    Text("${widget.gemMetadataText}", style: const TextStyle(fontSize: 16.0,)),
                    const SizedBox(height:12),
                    const Text("Video Capabilities", style: TextStyle(fontSize: 18.0, fontWeight: FontWeight.bold),),
                    Text("${widget.sensorVideoCapabilities}", style: const TextStyle(fontSize: 16.0,)),
                    const SizedBox(height:12),
                    const Text("Shoot Speed", style: TextStyle(fontSize: 18.0, fontWeight: FontWeight.bold),),
                    Text("${widget.contShootSpeed}", style: const TextStyle(fontSize: 16.0,)),
                    const SizedBox(height:12),
                    const Text("Focus System", style: TextStyle(fontSize: 18.0, fontWeight: FontWeight.bold),),
                    Text("${widget.autofocusSystem}", style: const TextStyle(fontSize: 16.0,)),
                    const SizedBox(height:12),
                    const Text("Connectivity", style: TextStyle(fontSize: 18.0, fontWeight: FontWeight.bold),),
                    Text("${widget.connectivity}", style: const TextStyle(fontSize: 16.0,)),
                    const SizedBox(height:12),
                    const Text("Camera Model", style: TextStyle(fontSize: 18.0, fontWeight: FontWeight.bold),),
                    Text("${widget.sensorLensMount}", style: const TextStyle(fontSize: 16.0,)),
                    const SizedBox(height:12),
                  ],
                ),
              )
            ],
          ),
          const SizedBox(height: 10.0),
        ],
      ),
    );
  }
}
