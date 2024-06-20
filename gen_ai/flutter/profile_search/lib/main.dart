import 'dart:ui';
import 'dart:convert';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:profile_search/views.dart';

import 'function.dart';

void main() {
  runApp(
    MaterialApp(
        home: App(),
        theme: ThemeData(
          primarySwatch: Colors.grey,
        )
    ),
  );
}

class App extends StatefulWidget {
  const App({super.key});

  @override
  State<App> createState() => _AppState();
}

class _AppState extends State<App> {
  var gridMapScann = [];
  var url = "";
  var text = "";
  var textInput = "";
  String logText = "";
  bool isVisible = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          Container(
            height: 65,
            decoration: BoxDecoration(
                border: const Border(bottom: BorderSide(color: Color(0xff333333))),
              color: Colors.blueGrey[50],
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Container(
                  height: 65,
                  width: 200,
                  margin: const EdgeInsets.only(left:40.0),
                  child: FittedBox(
                    child: Image.network(
                      "https://www.stagwellglobal.com/wp-content/uploads/2022/07/extended-logo.png",
                      scale:0.5,
                    ),
                  )
                ), //header
                Container(
                  margin: const EdgeInsets.only(right: 40.0),
                    child: const Center(
                        child: Text(
                            "view profile",
                          style: TextStyle(
                              color: Color(0xff333333),
                              fontWeight: FontWeight.bold,
                            decoration: TextDecoration.underline,
                          ),
                        )
                    )
                ),
              ],
            ),
          ),
          const SizedBox(height:25),
          Center(
            child: Container(
              alignment: Alignment.center,
              height:125,
              child: Column(
                children: [
                  const Text(
                      "Search for a colleague",
                    style: TextStyle(color: Color(0xff333333), fontSize: 20.0),
                    textAlign: TextAlign.start,
                  ),
                  SizedBox(height:10),
                  Container(
                    width: 600,
                    decoration: BoxDecoration(
                        border: Border.all(color: Colors.lightBlue, width: 1.5),
                      borderRadius: BorderRadius.circular(8.0),
                    ),
                    child: TextField(
                      decoration: const InputDecoration(
                        prefixIcon: Icon(Icons.search),
                        hintText: "Find your profile...",
                        border: InputBorder.none,
                      ),
                      onSubmitted: (value) async {
                        textInput = value.toString();
                        url = "http://localhost:8000/scann/"+textInput;
                        var decoded = await fetchdata(url);
                        var data = jsonDecode(decoded);
                        setState(() {
                          gridMapScann = data;
                          text = value;
                          logText = "Findings";
                          isVisible = true;
                        });
                      },
                    ),
                  ),
                  SizedBox(height:10),
                ],
              ),
            ),
          ),
          const SizedBox(height:10),
          if (isVisible)
            Row(
              children: [
                Expanded(
                  child: Container(
                      decoration: BoxDecoration(border: Border.all(color: Colors.black)),
                      alignment: Alignment.center,
                      child: Text("Name")
                  ),
                ),
                Expanded(
                  child: Container(
                      decoration: BoxDecoration(border: Border.all(color: Colors.black)),
                      alignment: Alignment.center,
                      child: Text("Company")
                  ),
                ),
                Expanded(
                  child: Container(
                      decoration: BoxDecoration(border: Border.all(color: Colors.black)),
                      alignment: Alignment.center,
                      child: Text("Job Title")
                  ),
                ),
                Expanded(
                  child: Container(
                      decoration: BoxDecoration(border: Border.all(color: Colors.black)),
                      alignment: Alignment.center,
                      child: Text("Location")
                  ),
                ),
              ],
            ),
          Container(
            height: 480,
              // decoration: BoxDecoration(border: Border.all(color: Colors.black)),
            child: ListView.builder(
                itemCount: gridMapScann.length,
                itemBuilder: (context, index) {
                  return Column(
                    children: [
                      Container(
                        // decoration: BoxDecoration(border: Border.all(color: Colors.black)),
                        height: 50.0,
                          //color: Colors.blueGrey[200],
                          child: EmployeesList(
                              name: gridMapScann.elementAt(index)["name"],
                              company: gridMapScann.elementAt(index)["company"],
                              job_title: gridMapScann.elementAt(index)["job_title"],
                              location: gridMapScann.elementAt(index)["location"],
                              gemini_summ: gridMapScann.elementAtOrNull(index)["gemini_summ"],
                          ),
                      ),
                    ],
                  );
                }

            )
          ),
        ],
      ),
    );
  }
}


