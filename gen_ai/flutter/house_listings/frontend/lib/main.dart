import 'dart:io';
import 'dart:convert';
import 'dart:typed_data';
import 'dart:html' as html;
import 'package:abnb/function.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter/cupertino.dart';
import 'package:path_provider/path_provider.dart';
import 'package:file_picker/file_picker.dart';
import 'package:video_player/video_player.dart';
import 'package:http_parser/http_parser.dart';
import 'package:image_picker/image_picker.dart';


import 'next_page.dart';

void main() {
  runApp(
    MaterialApp(
      home: MyApp(),
      theme: ThemeData(
        primarySwatch: Colors.pink,
      )
    ),
  );
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  VideoPlayerController? _controller;
  bool isVideoSelected = false;

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  List<String> pictureList=[
    "https://www.rocketmortgage.com/resources-cmsassets/RocketMortgage.com/Article_Images/Large_Images/Stock-Modern-House-In-Twilight-AdobeStock-368976934-copy.jpg",

  ];

  String text = "";
  String url = "";
  var text_input = "";
  var gridMap = [
    {
    "image_uri": "https://media.architecturaldigest.com/photos/61fc6aac9e1381243886999c/1:1/w_3679,h_3679,c_limit/Private%20Residence1207_1.jpg",
      "location": "New York"
    },
    {
      "image_uri": "https://cdn.thespaces.com/wp-content/uploads/2019/03/ART-DECO-HOME-FOR-SALE-Available-through-Belgium-Sothebys-International-Realty.jpg",
      "location": "Abu Dhabi"
    },
    {
      "image_uri": "https://images.seattletimes.com/wp-content/uploads/2015/11/c2cf3780-df36-11e4-9831-b297f2987e27.jpg?d=780x520",
      "location": "Dubai"
    },
    {
      "image_uri": "https://mir-s3-cdn-cf.behance.net/project_modules/fs/b8763e99526603.5ef4e13755a6e.jpg",
      "location": "Mexico"
    },
  ];
  var gridMapScann = [];
  var gridMapAll = [];
  String logText = "";
  Uint8List? _imageBytes;

  // List? get jsonResponse => [];
  var jsonResponse = [];

  Future<void> _pickImage() async {
    final ImagePicker picker = ImagePicker();
    final XFile? imageFile = await picker.pickVideo(source: ImageSource.gallery);
    // final tempDir = await getTemporaryDirectory();
    // final tempFile = File('${tempDir.path}/temp_video.mp4');



    if (imageFile != null) {
      final Uint8List bytes = await imageFile.readAsBytes();
      // text_input = "blue house";

      final blob = html.Blob([bytes]);
      final url = html.Url.createObjectUrlFromBlob(blob);

      _controller = VideoPlayerController.networkUrl(Uri.parse(url))
        ..initialize().then((_) {
          setState(() {
            isVideoSelected = true;
          });
          _controller!.play();
        });

      var request = http.MultipartRequest('POST', Uri.parse('http://localhost:8000/image'));

      request.files.add(
        http.MultipartFile.fromBytes(
          'file', // Match FastAPI parameter name
          bytes,
          filename: 'image.jpg',
          contentType: MediaType('image', 'jpeg'),
        ),
      );

      if (text_input != null && text_input.isNotEmpty) { // Only add if text is not null or empty
        request.fields['text_data'] = text_input;
      }

      var streamedResponse = await request.send();

      // 1. Check Response Status
      if (streamedResponse.statusCode == 200) {
        // 2. Read Response Body
        var response = await http.Response.fromStream(streamedResponse);
        String responseBody = response.body;

        // 3. Parse JSON
        try {
          var jsonResponse = jsonDecode(responseBody);
          setState(() {

            gridMapScann = List<Map<String, dynamic>>.from(jsonResponse);
            logText = "Findings";
          });

          // 4. Use the JSON Data
          print(jsonResponse);  // Or do whatever you need with the data

        } catch (e) {
          // Handle JSON parsing errors
          print('Error parsing JSON: $e');
        }
      } else {
        // Handle non-200 status codes (e.g., errors)
        print('Request failed with status: ${streamedResponse.statusCode}');
      }
      setState(() {
        _imageBytes = bytes;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: ListView(
        scrollDirection: Axis.vertical,
      children: [
        Container(
          height: 100,
          margin: const EdgeInsets.only(top: 2, right: 10.0, left: 20.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                "Groundbnb",
                style: TextStyle(
                  color: Color(0xffFF5A5F),
                  fontSize: 30.0,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(width: 30.0),
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    border: Border.all(color: const Color(0xffFF5A5F)),
                    borderRadius: const BorderRadius.only(
                        topLeft: Radius.circular(30.0),
                        bottomLeft: Radius.circular(30.0),
                        bottomRight: Radius.circular(30.0)
                    ),
                  ),
                  child: TextField(
                    decoration: InputDecoration(
                      prefixIcon: const Icon(Icons.search),
                      hintText: "Find a good place (Semantic Search)",
                      border: InputBorder.none,
                      suffixIcon: IconButton(
                        icon: const Icon(Icons.image), onPressed: _pickImage
                      ),
                    ),
                    onSubmitted: (value) async {
                      text_input = value.toString();
                      // url = "http://localhost:8000/scann/"+text_input;
                      // var decoded = await fetchdata(url);
                      // var data = jsonDecode(decoded);
                      setState(() {
                        // print(data[0]['host_name']);
                        // print(data[9]['host_name']);
                        // gridMapScann = data;
                        text = value;
                        logText = "Findings";
                      });
                    },
                  ),
                ),
              ),
              const SizedBox(width: 10.0),
              Stack(
                children: [
                  const Icon(Icons.notifications_none),
                  Positioned(
                    top:1,
                    right:1,
                    child: Container(
                      padding: EdgeInsets.all(2.0),
                      decoration: const BoxDecoration(
                        color: Colors.pinkAccent,
                        shape:BoxShape.circle,
                      ),
                      child: const Text(
                        "2",
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 10.0,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(width: 30.0),
              Container(
                width: 50.0,
                height: 50.0,
                decoration: const BoxDecoration(
                    shape: BoxShape.circle,
                    image: DecorationImage(
                        image: NetworkImage("https://www.rocketmortgage.com/resources-cmsassets/RocketMortgage.com/Article_Images/Large_Images/Stock-Modern-House-In-Twilight-AdobeStock-368976934-copy.jpg"),
                        fit: BoxFit.cover
                    )
                ),
              ),
            ],
          ),
        ),
        // Container(
        //   height:350,
        //   padding: const EdgeInsets.only(bottom: 10.0),
        //   decoration: BoxDecoration(
        //       border: Border(
        //           bottom: BorderSide(color: Colors.blueGrey.shade300)
        //       ),
        //   ),
        //   child: ListView.builder(
        //     scrollDirection: Axis.horizontal,
        //     itemCount: gridMap.length,
        //     itemBuilder: (BuildContext context, int index) {
        //       return homeWidget(
        //         image: "${gridMap.elementAt(index)["image_uri"]}",
        //         location: "${gridMap.elementAt(index)["location"]}"
        //       );
        //     },
        //   ),
        // ),
        // Container(
        //   height: 200,
        //   child: _imageBytes != null
        //       ? Image.memory(_imageBytes!)
        //       : Text(''),
        // ),
        if (isVideoSelected)
          SizedBox(
            height: 300,
            width: 400,
            child: AspectRatio(
                aspectRatio: _controller!.value.aspectRatio,
              child: VideoPlayer(_controller!),
            ),
          ),
        const SizedBox(height: 10),
        Container(
          padding: const EdgeInsets.all(12.0),
            child: Text(
                logText,
              style: const TextStyle(
                color: Colors.blueGrey,
                fontSize: 20.0,
              ),
            )
        ),
        Expanded(
          child: Container(
            padding: const EdgeInsets.all(12.0),
            height: 1000,
            child: GridView.builder(
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 5,
                  crossAxisSpacing: 15.0,
                  mainAxisSpacing: 50.0,
                  mainAxisExtent: 350,
                ),
                itemCount: gridMapScann.length,
                itemBuilder: (_, index) {
                  return Container(
                    decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(17.0,),
                        // border: Border.all(color: Colors.pinkAccent)
                    ),
                    child: Column(
                      children: [
                        ClipRRect(
                          borderRadius: const BorderRadius.only(
                            topLeft: Radius.circular(16.0),
                            topRight: Radius.circular(16.0),
                            bottomRight: Radius.circular(16.0),
                            bottomLeft: Radius.circular(16.0),
                          ),
                          child: InkWell(
                            child: Image.network(
                                "${gridMapScann.elementAt(index)["Img_interior_url_0"]}",
                                height: 200,
                                width: double.infinity,
                                fit: BoxFit.cover
                            ),
                            onTap: () {
                              Navigator.of(context).push(MaterialPageRoute(builder: (BuildContext context) {
                                return NextPage(
                                    image_uri_1: gridMapScann.elementAt(index)["Img_exterior_url_0"],
                                    image_uri_2: gridMapScann.elementAt(index)["Img_exterior_url_1"],
                                    image_uri_3: gridMapScann.elementAt(index)["Img_exterior_url_2"],
                                    image_uri_4: gridMapScann.elementAt(index)["Img_exterior_url_3"],
                                    image_uri_5: gridMapScann.elementAt(index)["Img_exterior_url_4"],
                                    image_uri_6: gridMapScann.elementAt(index)["Img_interior_url_0"],
                                    image_uri_7: gridMapScann.elementAt(index)["Img_interior_url_1"],
                                    image_uri_8: gridMapScann.elementAt(index)["Img_interior_url_2"],
                                    image_uri_9: gridMapScann.elementAt(index)["Img_interior_url_3"],
                                    image_uri_10: gridMapScann.elementAt(index)["Img_interior_url_4"],
                                    title: gridMapScann.elementAt(index)["title"],
                                    price_per_night: gridMapScann.elementAt(index)["price_per_night"],
                                    guests: gridMapScann.elementAt(index)["guests"],
                                    amenities: gridMapScann.elementAt(index)["amenities"],
                                    nearby_neighbourhood: gridMapScann.elementAt(index)["nearby_neighbourhood"],
                                );
                              }));
                            },
                          ),
                        ),
                        // Text(
                        //     "Gemini Detected Title: ${gridMapScann.elementAt(index)["title"]}",
                        //   style: const TextStyle(color: Color(0xffFF5A5F), fontWeight: FontWeight.bold),
                        // ),
                        const SizedBox(height: 8.0),
                        Text.rich(
                          textAlign: TextAlign.center,
                          TextSpan(
                            text: "Title: ",
                            style: const TextStyle(color: Color(0xffFF5A5F), fontWeight: FontWeight.bold),
                            children: <TextSpan>[
                              TextSpan(
                                  text: "${gridMapScann.elementAt(index)["title"]}",
                                style: const TextStyle(color: Colors.black, fontWeight: FontWeight.normal),

                              ),
                            ],
                          )
                        ),
                        Text.rich(
                            TextSpan(
                              text: "Rating: ",
                              style: const TextStyle(color: Color(0xffFF5A5F), fontWeight: FontWeight.bold),
                              children: <TextSpan>[
                                TextSpan(
                                  text: "${gridMapScann.elementAt(index)["rating"]}",
                                  style: const TextStyle(color: Colors.black, fontWeight: FontWeight.normal),
                                ),
                              ],
                            )
                        ),
                        Text.rich(
                            TextSpan(
                              text: "Location: ",
                              style: const TextStyle(color: Color(0xffFF5A5F), fontWeight: FontWeight.bold),
                              children: <TextSpan>[
                                TextSpan(
                                  text: "${gridMapScann.elementAt(index)["location"]}",
                                  style: const TextStyle(color: Colors.black, fontWeight: FontWeight.normal),
                                ),
                              ],
                            )
                        ),
                        Text.rich(
                            TextSpan(
                              text: "Host Guest: ",
                              style: const TextStyle(color: Color(0xffFF5A5F), fontWeight: FontWeight.bold),
                              children: <TextSpan>[
                                TextSpan(
                                  text: "${gridMapScann.elementAt(index)["host_name"]}",
                                  style: const TextStyle(color: Colors.black, fontWeight: FontWeight.normal),
                                ),
                              ],
                            )
                        ),
                      ],
                    ),
                  );
                }
            ),
          ),
        ),
      ],
      ),
    );
  }

  Widget homeWidget(
      {image, location}
      )
  {
    return Container(
      margin: const EdgeInsets.all(10.0),
      width: 250.0,
      height: 400.0,
      child: Stack(
        children: [
          Container(
            width: 230.0,
            height: 375.0,
            decoration: BoxDecoration(
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(30.0),
                bottomLeft: Radius.circular(30.0),
                bottomRight: Radius.circular(30.0),
              ),
              image: DecorationImage(
                  image: NetworkImage(image),
                  fit: BoxFit.cover
              ),
            ),
          ),
          Positioned(
            bottom:0,
            right:30.0,
            child: FloatingActionButton(
              mini: true,
              backgroundColor: const Color(0xffFF5A5F),
              child: const Icon(
                  Icons.chevron_right,
                  color: Colors.white),
              onPressed: (){},
            ),
          ),
          Positioned(
            bottom: 40,
            left: 20,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                const Text("Family House",
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Row(
                  children: <Widget>[
                    const Icon(Icons.location_on, color: Colors.white),
                    Text(
                      location,
                      style: const TextStyle(
                        color: Colors.white,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
Widget allWidget({image, location}){
  return Container(
    margin: const EdgeInsets.all(10.0),
    width: 250.0,
    height: 400.0,
    child: Stack(
      children: [
        Container(
          width: 230.0,
          height: 375.0,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.only(
              topLeft: Radius.circular(30.0),
              bottomLeft: Radius.circular(30.0),
              bottomRight: Radius.circular(30.0),
            ),
            image: DecorationImage(
                image: NetworkImage(image),
                fit: BoxFit.cover
            ),
          ),
        ),
        Positioned(
          bottom:0,
          right:30.0,
          child: FloatingActionButton(
            mini: true,
            backgroundColor: const Color(0xffFF5A5F),
            child: const Icon(
                Icons.chevron_right,
                color: Colors.white),
            onPressed: (){},
          ),
        ),
        Positioned(
          bottom: 40,
          left: 20,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              const Text("Family House",
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Row(
                children: <Widget>[
                  Icon(Icons.location_on, color: Colors.white),
                  Text(
                    location,
                    style: TextStyle(
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    ),
  );
}

class PageTwo extends StatefulWidget {
  final List<dynamic> gridMapAll;

  const PageTwo({super.key, required this.gridMapAll});

  @override
  State<PageTwo> createState() => _PageTwoState();
}
class _PageTwoState extends State<PageTwo> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Expanded(
        child: Container(
          padding: const EdgeInsets.only(right: 12.0, left: 12.0),
          color: Colors.grey[50],
          child: GridView.builder(
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 5,
                crossAxisSpacing: 15.0,
                mainAxisSpacing: 50.0,
                mainAxisExtent: 200,
              ),
              itemCount: widget.gridMapAll.length,
              itemBuilder: (_, index) {
                return Container(
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(17.0,),
                    border: Border.all(color: Colors.pinkAccent)
                  ),
                  child: Column(
                    children: [
                      ClipRRect(
                        borderRadius: const BorderRadius.only(
                          topLeft: Radius.circular(16.0),
                          topRight: Radius.circular(16.0),
                          bottomRight: Radius.circular(16.0),
                          bottomLeft: Radius.circular(16.0),
                        ),
                        child: Image.network(
                            "${widget.gridMapAll.elementAt(index)['image_uri']}",
                          height: 198,
                          width: double.infinity,
                          fit: BoxFit.cover
                        ),
                      )
                    ],
                  ),
                );
              }
              ),
        ),
      ),
    );
  }
}
