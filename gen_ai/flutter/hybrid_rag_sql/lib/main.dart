import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const MyApp());
}

class MessageBubble extends StatelessWidget {
  final String message;
  final bool isUserMessage;

  const MessageBubble({super.key, required this.message, required this.isUserMessage});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: isUserMessage ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 14),
        decoration: BoxDecoration(
          color: isUserMessage ? Colors.blue[200] : Colors.grey[300],
          borderRadius: BorderRadius.circular(15),
        ),
        child: Text(
          message,
          style: const TextStyle(fontSize: 16),
        ),
      ),
    );
  }
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.black),
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

  void _incrementCounter() {
    setState(() {
      _counter++;
    });
  }

  final List<String> chatbotHistory = <String>[];
  final ScrollController _scrollController = ScrollController();

  Future<Map<String, dynamic>> sendPostRequest(String text) async {
    final url = Uri.parse('http://127.0.0.1:8000/process/'); // Replace with your FastAPI endpoint

    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'text': text}), // Encode the JSON body
      );

      if (response.statusCode == 200) {
        // Successful response
        return jsonDecode(response.body); // Decode the JSON response
      } else {
        // Handle error responses
        print('Request failed with status: ${response.statusCode}.');
        return {'error': 'Request failed'}; // or throw an exception
      }
    } catch (e) {
      // Handle network or other errors
      print('Error during request: $e');
      return {'error': 'Network error'}; // or throw an exception
    }
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          Container(
            height:100,
            color: Colors.black,
          ),
          Expanded(
            child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: <Widget>[
                  Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: <Widget>[
                        Expanded(
                          child: Container(
                            alignment: Alignment.topCenter,
                            padding: const EdgeInsets.all(10),
                            margin: const EdgeInsets.only(top: 10, left: 10, bottom: 10),
                            width: 250,
                            decoration: BoxDecoration(
                              color: Colors.black,
                              border: Border.all(color: Colors.white54, width: 2),
                              borderRadius: const BorderRadius.all(
                                Radius.circular(10),
                              ),
                            ),
                            child: Column(
                              children: [
                                ElevatedButton(
                                    style: ElevatedButton.styleFrom(
                                        shape:  RoundedRectangleBorder(
                                            borderRadius: BorderRadius.circular(5.0)
                                        ),
                                        backgroundColor: Colors.white70,
                                        fixedSize: const Size(200, 40),
                                        foregroundColor: Colors.black,
                                        textStyle: const TextStyle(fontWeight: FontWeight.bold)
                                    ),
                                    onPressed: () {
                                      print("text");
                                    },
                                    child: const Text('Retail')
                                )
                              ],
                            ),
                          ),
                        ),
                      ]
                  ),
                  Expanded(
                    child: Container(
                        margin: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: Colors.white30,
                          border: Border.all(color: Colors.black, width: 2),
                          borderRadius: const BorderRadius.all(
                            Radius.circular(10),
                          ),
                        ),
                        child: ListView.builder(
                            controller: _scrollController,
                            itemCount: chatbotHistory.length,
                            itemBuilder: (BuildContext context, int index) {
                              bool isUserMessage = index % 2 == 0;
                              return MessageBubble(
                                message: chatbotHistory[index],
                                isUserMessage: isUserMessage,
                              );
                            }
                        )
                    ),
                  ),
                  Column(
                    children: [
                      Expanded(
                        child: Container(
                            padding: const EdgeInsets.all(10),
                            margin: const EdgeInsets.only(top: 10, right: 10, bottom: 10),
                            width: 350,
                            decoration: BoxDecoration(
                              color: Colors.black,
                              border: Border.all(color: Colors.white54, width: 2),
                              borderRadius: const BorderRadius.all(
                                Radius.circular(10),
                              ),
                            ),
                            child: const Text("")
                        ),
                      ),
                    ],
                  )
                ]
            ),
          ),
          Container(
              color: const Color(0x2C7EE22C),
              height: 50,
              margin: const EdgeInsets.all(10),
              child: TextField(
                onSubmitted: (String value) async {
                  print("Submitted: $value");
                  var re = await sendPostRequest(value);
                  print(re);

                  setState(() {
                    chatbotHistory.add(value);
                    chatbotHistory.add(re["response"]);
                    WidgetsBinding.instance.addPostFrameCallback((_) {
                      _scrollController.animateTo(
                        _scrollController.position.maxScrollExtent,
                        duration: const Duration(milliseconds: 300),
                        curve: Curves.easeOut,
                      );
                    });
                  });
                },
                decoration: const InputDecoration(
                    border: OutlineInputBorder(),
                    labelText: 'Sup!'
                ),
              )
          )
        ],
      ), // This trailing comma makes auto-formatting nicer for build methods.
    );
  }
}