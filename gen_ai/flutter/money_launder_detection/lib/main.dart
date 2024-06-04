import 'dart:collection';
import 'dart:convert';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:animated_text_kit/animated_text_kit.dart';

import 'function.dart';

void main() => runApp(const Page());

class Page extends StatelessWidget {
  const Page({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      home: Scaffold(
        body: View(),
      ),
    );
  }
}

class View extends StatefulWidget {
  const View({super.key});

  @override
  State<View> createState() => _ViewState();
}

class _ViewState extends State<View> {
  List<String> messagesList = [];
  String url = '';
  TextEditingController segment = TextEditingController(text: "0");
  TextEditingController step = TextEditingController(text: "2");
  TextEditingController trans_type = TextEditingController(text: "WIRE_OUT");
  TextEditingController amount = TextEditingController(text: "18627.02");
  TextEditingController nameOrig = TextEditingController(text: "C1375503918");
  TextEditingController oldbalanceOrg = TextEditingController(text: "18627.02");
  TextEditingController nameDest = TextEditingController(text: "C234430897");
  TextEditingController oldbalanceDest = TextEditingController(text: "0.0");
  TextEditingController accountType = TextEditingController(text: "FOREIGN");
  var sub_text = '';
  // var llmContext = <String, dynamic>{};
  String llmContext = '';
  var text_input = '';
  String text_prompt = '';

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.only(left:10, right:10, top: 20, bottom: 20),
              height: 600,
              width: 400,
              decoration: BoxDecoration(color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.grey)
              ),
              child:
              ListView.builder(
                shrinkWrap: true,
                padding: const EdgeInsets.only(top:15),
                itemCount: messagesList.length,
                itemBuilder: (context, index) {
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: UnmodifiableListView([
                      const SizedBox(height:10),
                      const Text(
                        "Gemini",
                        style: TextStyle(color: Colors.purple, fontWeight: FontWeight.w700),
                      ),
                      const SizedBox(height: 10),
                      Container(
                        padding: const EdgeInsets.all(15.0),
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(12),
                          // color: const Color(0xff1a3059),
                          color: Colors.blueAccent,
                        ),
                        child:                           DefaultTextStyle(
                          style: const TextStyle(color: Colors.white),
                          child: AnimatedTextKit(
                            totalRepeatCount: 1,
                            animatedTexts: [
                              TypewriterAnimatedText(messagesList.elementAt(index))
                            ],
                          ),
                        ),
                      ),
                    ]),
                  );
                },
              ),
            ),
            const SizedBox(height: 10),
            Container(
                padding: const EdgeInsets.only(left:10, right:10, top:25, bottom: 25),
                height: 100,
                width: 400,
                decoration: BoxDecoration(color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.grey),
                ),
                child: TextField(
                  style: const TextStyle(color: Colors.black),
                  decoration: const InputDecoration(
                    hintText: "Write something",
                    hintStyle: TextStyle(color: Colors.black),
                    border: OutlineInputBorder(
                        borderSide: BorderSide(color: Colors.grey)
                    ),
                  ),
                  onSubmitted: (value) async {
                    text_input = value.toString();
                    url = 'http://127.0.0.1:8002/bot?prompt=$text_input&context=$llmContext';
                    var decoded = await fetchdata(url);
                    text_prompt = jsonDecode(decoded);
                    setState(() {
                      messagesList.add(text_prompt);
                    });
                  },
                )
            )
          ],
        ),
        const SizedBox(width: 10),
        Container(
          height: 710,
          width: 200,
          decoration: BoxDecoration(
              color: Colors.grey[100],
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.grey)
          ),
          child: ListView(
            padding: const EdgeInsets.only(left: 10.0, right: 10.0, top:20),
            children:  [
              Title(color: Colors.black, child: const Text("Parameters")),
              const SizedBox(height: 20,),
              TextFormField(
                controller: segment,
                style: const TextStyle(fontSize: 12),
                textAlign: TextAlign.center,
                decoration: const InputDecoration(
                  filled: true,
                  fillColor: Colors.white,
                  labelText: "segment",
                  labelStyle: TextStyle(
                      fontSize: 12,
                      color: Colors.blueAccent
                  ),
                  isDense: true,
                  contentPadding: EdgeInsets.all(8),
                  border: OutlineInputBorder(borderSide: BorderSide(color: Colors.black)),
                ),
              ),
              const SizedBox(height: 16,),
              TextFormField(
                controller: step,
                style: const TextStyle(fontSize: 12),
                textAlign: TextAlign.center,
                decoration: const InputDecoration(
                  filled: true,
                  fillColor: Colors.white,
                  labelText: "step",
                  labelStyle: TextStyle(
                      fontSize: 12,
                      color: Colors.blueAccent
                  ),
                  isDense: true,
                  contentPadding: EdgeInsets.all(8),
                  border: OutlineInputBorder(borderSide: BorderSide(color: Colors.black)),
                ),
              ),
              const SizedBox(height: 16,),
              TextFormField(
                controller: trans_type,
                style: TextStyle(fontSize: 12),
                textAlign: TextAlign.center,
                decoration: const InputDecoration(
                  filled: true,
                  fillColor: Colors.white,
                  labelText: "trans_type",
                  labelStyle: TextStyle(
                      fontSize: 12,
                      color: Colors.blueAccent
                  ),
                  isDense: true,
                  contentPadding: EdgeInsets.all(8),
                  border: OutlineInputBorder(borderSide: BorderSide(color: Colors.black)),
                ),
              ),
              const SizedBox(height: 16,),
              TextFormField(
                controller: amount,
                style: const TextStyle(fontSize: 12),
                textAlign: TextAlign.center,
                decoration: const InputDecoration(
                  filled: true,
                  fillColor: Colors.white,
                  labelText: "amount",
                  labelStyle: TextStyle(
                      fontSize: 12,
                      color: Colors.blueAccent
                  ),
                  isDense: true,
                  contentPadding: EdgeInsets.all(8),
                  border: OutlineInputBorder(borderSide: BorderSide(color: Colors.black)),
                ),
              ),
              const SizedBox(height: 16,),
              TextFormField(
                controller: nameOrig,
                style: const TextStyle(fontSize: 12),
                textAlign: TextAlign.center,
                decoration: const InputDecoration(
                  filled: true,
                  fillColor: Colors.white,
                  labelText: "nameOrig",
                  labelStyle: TextStyle(
                      fontSize: 12,
                      color: Colors.blueAccent
                  ),
                  isDense: true,
                  contentPadding: EdgeInsets.all(8),
                  border: OutlineInputBorder(borderSide: BorderSide(color: Colors.black)),
                ),
              ),
              const SizedBox(height: 16,),
              TextFormField(
                controller: oldbalanceOrg,
                style: const TextStyle(fontSize: 12),
                textAlign: TextAlign.center,
                decoration: const InputDecoration(
                  filled: true,
                  fillColor: Colors.white,
                  labelText: "oldbalanceOrg",
                  labelStyle: TextStyle(
                      fontSize: 12,
                      color: Colors.blueAccent
                  ),
                  isDense: true,
                  contentPadding: EdgeInsets.all(8),
                  border: OutlineInputBorder(borderSide: BorderSide(color: Colors.black)),
                ),
              ),
              const SizedBox(height: 16,),
              TextFormField(
                controller: nameDest,
                style: const TextStyle(fontSize: 12),
                textAlign: TextAlign.center,
                decoration: const InputDecoration(
                  filled: true,
                  fillColor: Colors.white,
                  labelText: "nameDest",
                  labelStyle: TextStyle(
                      fontSize: 12,
                      color: Colors.blueAccent
                  ),
                  isDense: true,
                  contentPadding: EdgeInsets.all(8),
                  border: OutlineInputBorder(borderSide: BorderSide(color: Colors.black)),
                ),
              ),
              const SizedBox(height: 16,),
              TextFormField(
                controller: oldbalanceDest,
                style: const TextStyle(fontSize: 12),
                textAlign: TextAlign.center,
                decoration: const InputDecoration(
                  filled: true,
                  fillColor: Colors.white,
                  labelText: "oldbalanceDest",
                  labelStyle: TextStyle(
                      fontSize: 12,
                      color: Colors.blueAccent
                  ),
                  isDense: true,
                  contentPadding: EdgeInsets.all(8),
                  border: OutlineInputBorder(borderSide: BorderSide(color: Colors.black)),
                ),
              ),
              const SizedBox(height: 16,),
              TextField(
                controller: accountType,
                style: const TextStyle(fontSize: 12),
                textAlign: TextAlign.center,
                decoration: const InputDecoration(
                  filled: true,
                  fillColor: Colors.white,
                  labelText: "accountType",
                  labelStyle: TextStyle(
                      fontSize: 12,
                      color: Colors.blueAccent
                  ),
                  isDense: true,
                  contentPadding: EdgeInsets.all(8),
                  border: OutlineInputBorder(borderSide: BorderSide(color: Colors.black)),
                ),
              ),
              const SizedBox(height: 20),
              ElevatedButton(onPressed: () {
                setState(() {
                  // llmContext = {
                  //   "segment": segment.text,
                  //   "step": step.text,
                  //   "trans_type": trans_type.text,
                  //   "amount": amount.text,
                  //   "nameOrig": nameOrig.text,
                  //   "oldbalanceOrg": oldbalanceOrg.text,
                  //   "nameDest": nameDest.text,
                  //   "oldbalanceDest": oldbalanceDest,
                  //   "accountType": accountType.text,
                  // };
                  llmContext = "segment: ${segment.text}, step: ${step.text}, trans_type: ${trans_type.text}, amount: ${amount.text}, nameOrig: ${nameOrig.text}"
                      " oldbalanceOrg: ${oldbalanceOrg.text}, nameDest: ${nameDest.text}, oldbalanceOrg: ${oldbalanceOrg.text}, nameDest: ${nameDest.text},"
                      " oldbalanceDest: ${oldbalanceDest.text}, accountType: ${accountType.text}";
                  sub_text = "Submitted!";
                });

              },
                child: const Text("Submit"),
              ),
              const SizedBox(height:20,),
              Text(sub_text)
            ],
          ),
        )
      ],
    );
  }
}