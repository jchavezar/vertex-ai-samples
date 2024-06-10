import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const MyHomePage(title: 'Flutter Demo Home Page'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  int _counter = 0;
  var url = "";
  var textInput = "";
  late final TextEditingController _messageController;
  final FocusNode _focusNode = FocusNode();
  List<Map> messages = [];

  void _incrementCounter() {
    setState(() {
      _counter++;
    });
  }

  @override
  void initState() {
    _messageController = TextEditingController();
    super.initState();
  }

  @override
  void dispose() {
    _messageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 12,
        ),
            child: Column(
              children: [
                Expanded(
                  child: ListView.builder(
                    itemCount: messages.length,
                      itemBuilder: (context, index) {
                        final message = messages.elementAt(index);
                        return Align(
                          alignment: message["user"]  == "mine" ? Alignment.centerRight: Alignment.centerLeft,
                          child: Container(
                            margin: const EdgeInsets.symmetric(vertical: 4.0, horizontal: 8.0),
                            padding: const EdgeInsets.all(12.0),
                            decoration: BoxDecoration(
                              color: message["user"]  == "mine" ? Colors.blueAccent : Colors.grey[300],
                              borderRadius: BorderRadius.circular(16.0),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  message["user"]  == "mine" ? message["message"]  : message["response"]["response"],
                                  style: TextStyle(
                                    color: message["user"]  == "mine" ? Colors.white: Colors.black,
                                    fontSize: 16.0,
                                  ),
                                ),
                                const SizedBox(height: 2.0),
                                if(message["user"] != "mine" && message["response"]["image_required"] == "true")
                                  const Column(
                                    children: [
                                      SizedBox(height: 4.0),
                                      ElevatedButton(
                                        onPressed: null,
                                        child: Text("Upload"),
                                      ),
                                    ],
                                  ),
                                const SizedBox(height: 10),
                              ],
                            ),
                          ),
                        );
                      }
                      )
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 3
                  ),
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
                  child: Row(
                    children: [
                      Expanded(
                          child: TextField(
                            controller: _messageController,
                            focusNode: _focusNode,
                            decoration: const InputDecoration(
                              border: InputBorder.none,
                              hintText: "Write something...",
                            ),
                            onSubmitted: (value) async {
                              textInput = value.toString();
                              messages.add({"user": "mine", "message": textInput});
                              setState((){});
                              url = "http://localhost:8000/query";
                              var request = http.MultipartRequest('POST', Uri.parse(url));
                              request.fields['text_data'] = textInput;
                              var streamedResponse = await request.send();
                              if (streamedResponse.statusCode == 200) {
                                var response = await http.Response.fromStream(streamedResponse);
                                String responseBody = response.body;

                                try {
                                  var jsonResponse = jsonDecode(responseBody);
                                  // for (var response in List<Map<String, dynamic>>.from(jsonResponse)) {
                                  //   _context.add(response['description']);
                                  // }

                                  messages.add({"user": "gemini", "response": json.decode(jsonResponse["message"])});

                                  setState(() {
                                    print("testing");
                                    print(messages);
                                    print(messages[1]["response"]["image_required"]);
                                    print(messages[1]["response"]["image_required"].runtimeType);
                                    print("done");

                                  });
                                  _messageController.clear();
                                  _focusNode.requestFocus();
                                } catch (e) {
                                  print('Error parsing JSON: $e');
                                }
                              } else {
                                print('Request failed with status: ${streamedResponse.statusCode}');
                              }
                            },
                            // onSubmitted: () async {
                            //   final message = _messageController.text.trim();
                            //   if (message.isEmpty) return;
                            //   await SendMessage
                            // },
                          )
                      ),
                      IconButton(
                        onPressed: () {},
                        icon: const Icon(Icons.image)
                      ),
                      IconButton(
                          onPressed: () {},
                          icon: const Icon(Icons.send)
                      )
                    ],
                  ),
                ),
              ],
            ),
      ),
      // floatingActionButton: FloatingActionButton(
      //   onPressed: _incrementCounter,
      //   tooltip: 'Increment',
      //   child: const Icon(Icons.add),
      // ), // This trailing comma makes auto-formatting nicer for build methods.
    );
  }
}
