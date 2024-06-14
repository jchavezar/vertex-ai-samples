import 'dart:convert';
// import 'next_page.dart';
import 'dart:html' as html;
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:video_player/video_player.dart';
import 'package:http_parser/http_parser.dart';
import 'package:image_picker/image_picker.dart';
import 'package:google_generative_ai/google_generative_ai.dart';

import 'next_page.dart';

void main() {
  runApp(
    MaterialApp(
        home: const MyApp(),
        theme: ThemeData(
          // primarySwatch: Colors.black,
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
  var _textInput = "";
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
  List chatMessages = [];
  String logText = "";
  String modelResponse = "";
  String banner = "Ok lets check what we have. Please Wait...";
  bool _isBold = false;
  bool _showRow = false;
  final List<dynamic> _context = [];

  // List? get jsonResponse => [];
  var jsonResponse = [];
  static const apiKey = String.fromEnvironment('API_KEY');

  Future<void> _pickImage() async {
    final ImagePicker picker = ImagePicker();
    final XFile? imageFile = await picker.pickVideo(source: ImageSource.gallery);
    // final tempDir = await getTemporaryDirectory();
    // final tempFile = File('${tempDir.path}/temp_video.mp4');

    if (imageFile != null) {
      final Uint8List bytes = await imageFile.readAsBytes();
      // _textInput = "blue house";

      final blob = html.Blob([bytes]);
      final url = html.Url.createObjectUrlFromBlob(blob);

      setState(() {
        isVideoSelected = true;
        _controller = VideoPlayerController.networkUrl(Uri.parse(url));
      });

      _controller!.initialize().then((_) {
        setState(() {}); // Might be redundant if video automatically updates on play
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

      if (_textInput != "" && _textInput.isNotEmpty) { // Only add if text is not null or empty
        request.fields['text_data'] = _textInput;
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

          for (var response in List<Map<String, dynamic>>.from(jsonResponse)) {
            _context.add(response['description']);
          }
          var prompt = '''From the following context give me a catchy summary about the listings:
          
          <rules>
          1. Detect the input $_textInput language and respond in that language.
          2. Use the same language in your _textInput (input).
          </rules>
          
          <context>
          $_context
          </context>
          
          Response as raw text<String>:''';
          _sendMessage(prompt);

          setState(() {
            gridMapScann = List<Map<String, dynamic>>.from(jsonResponse);
            logText = "Findings";
            _showRow = _textInput.isNotEmpty;
          });

          // 4. Use the JSON Data

        } catch (e) {
          // Handle JSON parsing errors
          if (kDebugMode) {
            print('Error parsing JSON: $e');
          }
        }
      } else {
        // Handle non-200 status codes (e.g., errors)
        if (kDebugMode) {
          print('Request failed with status: ${streamedResponse.statusCode}');
        }
      }
      setState(() {
      });
    }
  }

  final _textController = TextEditingController();
  final model = GenerativeModel(
    model: 'gemini-1.5-flash-latest',
    apiKey: apiKey,
  );
  late final content = "";

  Future<void> _sendMessage(prompt) async {

    final re = await model.generateContent([Content.text(prompt)]);
    setState(() {
      final phrases = re.text!.split('\n\n');
      final formattedPhrases = phrases.where((phrase) => phrase.isNotEmpty).join('\n\n');
      chatMessages.add(formattedPhrases);
      _isBold = !_isBold;
      banner = "Gemini Response";
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: ListView(
        scrollDirection: Axis.vertical,
        children: [
          Container(
            height: 50,
            margin: const EdgeInsets.only(left: 35.0, right: 45.0, top: 10.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Padding(
                  padding: const EdgeInsets.all(5.0),
                  child: Image.network(
                      "https://global.canon/en/corporate/logo/img/logo_01.png"
                  ),
                ),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Get your camera!',
                      style: TextStyle(
                        fontSize: 15,
                      ),
                    ),
                    Row(
                      children: [
                        const SizedBox(width: 16),
                        const Icon(Icons.language),
                        const SizedBox(width: 16),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 8,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.grey[300],
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: const Row(
                            children: [
                              Icon(Icons.menu),
                              SizedBox(width: 16),
                              Icon(Icons.person),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ],
                )
              ],
            ),
          ),
          Container(
            height: 120,
            margin: const EdgeInsets.only(top: 2, right: 10.0, left: 20.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Expanded(child: SizedBox(width: 40.0)),
                SizedBox(
                  width: 750,
                  child: TextField(
                    minLines: 1,
                    maxLines: 10,
                    textInputAction: TextInputAction.done,
                    controller: _textController,
                    style: const TextStyle(fontSize: 27.0, height: 2.0),
                    decoration: InputDecoration(
                      hintText: 'Search cameras',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(30.0),
                        borderSide: BorderSide.none,
                      ),
                      filled: true,
                      fillColor: Colors.grey[100], // Light grey background
                      prefixIcon: const Icon(Icons.search), // Leading search icon
                      prefixIconConstraints: const BoxConstraints(
                        minWidth: 60, // Adjust as needed
                      ),
                      suffixIconConstraints: const BoxConstraints(
                        minWidth: 80, // Adjust as needed
                      ),
                      contentPadding: const EdgeInsets.symmetric(vertical: 15.0, horizontal: 50.0),
                      suffixIcon: IconButton(
                          icon: const Icon(Icons.video_file), onPressed: _pickImage
                      ),
                    ),
                    onChanged: (value) async {
                      _textInput = value.toString();
                      setState(() {

                      });
                    },
                    onSubmitted: (value) async {
                      _textInput = value.toString();

                      var url = isVideoSelected
                          ? 'http://localhost:8000/image'
                          : 'https://rag-mem-oyntfgdwsq-uc.a.run.app/embeddings';

                      if (!isVideoSelected && _textInput.isNotEmpty) {

                        // Set the headers for JSON content
                        // var headers = {'Content-Type': 'application/json'};
                        var headers = {
                          'Content-Type': 'application/json',
                        };
                        var body = jsonEncode({
                          'query': _textInput,
                        });
                        var response = await http.post(
                          Uri.parse(url),
                          headers: headers,
                          body: body, // Encode the JSON data
                        );
                        if (response.statusCode == 200) {
                          // Successful request: Handle the response data (e.g., JSON parsing)
                          // final data = json.decode(response.body);
                          final data = jsonDecode(response.body);


                          for (var response in List<Map<String, dynamic>>.from(data)) {
                                _context.add(response['gem_metadata_text']);
                              }
                          var prompt = '''From the following context give me a catchy summary about the listings,

                            <context>
                            $_context
                            </context>

                            <constraints>
                            1. Do not use Markdown in your response.
                            </constraints>

                            Response:''';
                          _sendMessage(prompt);
                          setState(() {
                            gridMapScann = List<Map<String, dynamic>>.from(data);
                            logText = "Findings";
                            _showRow = true;
                          });
                          // Process the data...
                        } else {
                          // Handle errors (e.g., 400 Bad Request, 500 Internal Server Error)
                          if (kDebugMode) {
                            print('Request failed with status: ${response.statusCode}');
                          }
                          if (kDebugMode) {
                            print('Error message: ${response.body}');
                          }
                        }
                      }
                    },
                  ),
                ),
                const Expanded(child: SizedBox(width: 30.0)),
              ],
            ),
          ),
          const SizedBox(height:20),
          if (isVideoSelected)
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  padding: const EdgeInsets.only(top: 10.0, bottom: 10.0, left:20.0, right: 20.0),
                  height: 350,
                  width: 600,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(12.0),
                    color: Colors.grey[100],
                  ),
                  alignment: Alignment.topLeft,
                  child: Column(
                    children: [
                      SizedBox(
                        height: 40.0,
                        child: Row(
                          children: [
                            const Icon(Icons.science, color: Colors.blue), // Or use font_awesome_flutter
                            Text(
                              banner,
                              style: TextStyle(fontWeight: _isBold ? FontWeight.bold : FontWeight.normal
                              ),
                            ),
                            const SizedBox(width: 8),
                            const Icon(Icons.arrow_drop_down, color: Colors.blue),
                          ],
                        ),
                      ),
                      Expanded(
                        child: ListView.builder(
                          itemCount: chatMessages.length,
                          itemBuilder: (BuildContext context, int index) {
                            final message = chatMessages[index];
                            return Container(
                              padding: const EdgeInsets.all(8.0),
                              margin: const EdgeInsets.symmetric(vertical:4.0),
                              decoration: BoxDecoration(
                                color: Colors.grey[200],
                                borderRadius: BorderRadius.circular(12.0),
                              ),
                              child: Text(
                                message,
                                style: const TextStyle(fontSize: 18.0),
                              ),
                            );
                          },
                        ),
                      ),
                      const SizedBox(height:10.0),
                      Container(
                        height: 60.0,
                        alignment: Alignment.center,
                        child: TextField(
                          decoration: InputDecoration(
                            hintText: "Ask follow up",
                            fillColor: Colors.white,
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(30.0),
                              borderSide: BorderSide.none,
                            ),
                            filled: true,
                            enabledBorder: OutlineInputBorder( // When not in focus
                              borderRadius: BorderRadius.circular(30.0),
                              borderSide: BorderSide.none,
                            ),
                          ),
                          onSubmitted: (value) {
                            var query = value.toString();
                            var prompt = """Respond the question using the following context:
                          <rules>
                          1. Answer as raw text (not markdown).

                          </rules>
                          
                          <Context>
                          $gridMapScann
                          </Context>
                          
                          Question: $query""";
                            _sendMessage(prompt);
                          },
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 20),
                Container(
                  height: 350,
                  width: 600,
                  decoration: BoxDecoration(borderRadius: BorderRadius.circular(12.0)),
                  alignment: Alignment.center,
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(12.0),
                    child: AspectRatio(
                      aspectRatio: _controller!.value.aspectRatio,
                      child: VideoPlayer(_controller!),
                    ),
                  ),
                ),
              ],
            ),
          if (_showRow && !isVideoSelected)
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  padding: const EdgeInsets.only(top: 10.0, bottom: 10.0, left:20.0, right: 20.0),
                  height: 350,
                  width: 800,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(12.0),
                    color: Colors.grey[100],
                  ),
                  alignment: Alignment.topLeft,
                  child: Column(
                    children: [
                      SizedBox(
                        height: 40.0,
                        child: Row(
                          children: [
                            const Icon(Icons.science, color: Colors.blue), // Or use font_awesome_flutter
                            Text(
                              banner,
                              style: TextStyle(fontWeight: _isBold ? FontWeight.bold : FontWeight.normal
                              ),
                            ),
                            const SizedBox(width: 8),
                            const Icon(Icons.arrow_drop_down, color: Colors.blue),
                          ],
                        ),
                      ),
                      Expanded(
                        child: ListView.builder(
                          itemCount: chatMessages.length,
                          itemBuilder: (BuildContext context, int index) {
                            final message = chatMessages[index];
                            return Container(
                              padding: const EdgeInsets.all(8.0),
                              margin: const EdgeInsets.symmetric(vertical:4.0),
                              decoration: BoxDecoration(
                                color: Colors.grey[200],
                                borderRadius: BorderRadius.circular(12.0),
                              ),
                              child: Text(
                                message,
                                style: const TextStyle(fontSize: 18.0),
                              ),
                            );
                          },
                        ),
                      ),
                      const SizedBox(height:10.0),
                      Container(
                        height: 60.0,
                        alignment: Alignment.center,
                        child: TextField(
                          decoration: InputDecoration(
                            hintText: "Ask follow up",
                            fillColor: Colors.white,
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(30.0),
                              borderSide: BorderSide.none,
                            ),
                            filled: true,
                            enabledBorder: OutlineInputBorder( // When not in focus
                              borderRadius: BorderRadius.circular(30.0),
                              borderSide: BorderSide.none,
                            ),
                          ),
                          onSubmitted: (value) {
                            var query = value.toString();
                            var prompt = """Respond the question using the following context:
                          
                          <Context>
                          $gridMapScann
                          </Context>
                          
                          Question: $query""";
                            _sendMessage(prompt);
                          },
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          const SizedBox(height: 10),
          Container(
              padding: const EdgeInsets.all(12.0),
              child: Text(
                logText,
                style: const TextStyle(
                  color: Colors.blueGrey,
                  fontSize: 22.0,
                ),
              )
          ),
          Container(
            padding: const EdgeInsets.all(12.0),
            height: 1000,
            child: GridView.builder(
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 4,
                  crossAxisSpacing: 15.0,
                  mainAxisSpacing: 50.0,
                  mainAxisExtent: 360,
                ),
                itemCount: gridMapScann.length,
                itemBuilder: (_, index) {
                  return Container(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(17.0,),
                      // border: Border.all(color: Colors.pinkAccent)
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
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
                                "${gridMapScann.elementAt(index)["image_gcs_uri"]}",
                                height: 200,
                                width: double.infinity,
                                fit: BoxFit.cover
                            ),
                            onTap: () {
                              Navigator.of(context).push(MaterialPageRoute(builder: (BuildContext context) {
                                return NextPage(
                                  imageGcsUri: gridMapScann.elementAt(index)["image_gcs_uri"],
                                  sensorLensMount: gridMapScann.elementAt(index)["sensor_lens_mount"],
                                  sensorType: gridMapScann.elementAt(index)["sensor_type"],
                                  sensorResolution: gridMapScann.elementAt(index)["sensor_resolution"],
                                  sensorImageStabilization: gridMapScann.elementAt(index)["sensor_image_stabilization"],
                                  sensorVideoCapabilities: gridMapScann.elementAt(index)["sensor_video_capabilities"],
                                  contShootSpeed: gridMapScann.elementAt(index)["continuous_shoot_speed"],
                                  autofocusSystem: gridMapScann.elementAt(index)["autofocus_system"],
                                  isoRange: gridMapScann.elementAt(index)["iso_range"],
                                  connectivity: gridMapScann.elementAt(index)["connectivity"],
                                  gemMetadataText: gridMapScann.elementAt(index)["gem_metadata_text"],
                                  summary: gridMapScann.elementAt(index)["summary"],
                                );
                              }));
                            },
                          ),
                        ),
                        const SizedBox(height: 8.0),
                        // Text.rich(
                        //   textAlign: TextAlign.center,
                        //   TextSpan(
                        //     text: "Title: ",
                        //     style: const TextStyle(color: Color(0xffFF5A5F), fontWeight: FontWeight.bold),
                        //     children: <TextSpan>[
                        //       TextSpan(
                        //           text: "${gridMapScann.elementAt(index)["title"]}",
                        //         style: const TextStyle(color: Colors.black, fontWeight: FontWeight.normal),
                        //
                        //       ),
                        //     ],
                        //   )
                        // ),
                        // Text.rich(
                        //     TextSpan(
                        //       text: "Rating: ",
                        //       style: const TextStyle(color: Color(0xffFF5A5F), fontWeight: FontWeight.bold),
                        //       children: <TextSpan>[
                        //         TextSpan(
                        //           text: "${gridMapScann.elementAt(index)["rating"]}",
                        //           style: const TextStyle(color: Colors.black, fontWeight: FontWeight.normal),
                        //         ),
                        //       ],
                        //     )
                        // ),
                        // Text.rich(
                        //     TextSpan(
                        //       text: "Location: ",
                        //       style: const TextStyle(color: Color(0xffFF5A5F), fontWeight: FontWeight.bold),
                        //       children: <TextSpan>[
                        //         TextSpan(
                        //           text: "${gridMapScann.elementAt(index)["location"]}",
                        //           style: const TextStyle(color: Colors.black, fontWeight: FontWeight.normal),
                        //         ),
                        //       ],
                        //     )
                        // ),
                        // Text.rich(
                        //     TextSpan(
                        //       text: "Host Guest: ",
                        //       style: const TextStyle(color: Color(0xffFF5A5F), fontWeight: FontWeight.bold),
                        //       children: <TextSpan>[
                        //         TextSpan(
                        //           text: "${gridMapScann.elementAt(index)["host_name"]}",
                        //           style: const TextStyle(color: Colors.black, fontWeight: FontWeight.normal),
                        //         ),
                        //       ],
                        //     )
                        // ),,
                        Padding(
                          padding: const EdgeInsets.only(left: 6.0, right: 6.0),
                          child: Row(
                            children: [
                              Text(
                                gridMapScann.elementAt(index)["sensor_type"],
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 18,
                                ),
                              ),
                              const Spacer(),
                              const Icon(Icons.star, color: Colors.black),
                              Text(gridMapScann.elementAt(index)["sensor_resolution"].toString()),
                            ],
                          ),
                        ),
                        const SizedBox(height: 4),
                        Padding(
                          padding: const EdgeInsets.only(left: 6.0, right: 6.0),
                          child: Text(
                            gridMapScann.elementAt(index)["sensor_image_stabilization"],
                            style: const TextStyle(
                              fontSize: 17,
                              color: Colors.grey,
                            ),
                          ),
                        ),
                        const SizedBox(height: 4),
                        Padding(
                          padding: const EdgeInsets.only(left: 6.0, right: 6.0),
                          child: Text(
                            "\$ ${gridMapScann.elementAt(index)["sensor_video_capabilities"]}",
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 15,
                            ),
                          ),
                        ),
                      ],
                    ),
                  );
                }
            ),
          ),
        ],
      ),
    );
  }
}

