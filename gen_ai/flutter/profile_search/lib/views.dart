import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';

class EmployeesList extends StatelessWidget {
  final String name;
  final String company;
  final String job_title;
  final String location;
  final String gemini_summ;

  EmployeesList({
    super.key,
    required this.name,
    required this.company,
    required this.job_title,
    required this.location,
    required this.gemini_summ,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: InkWell(
            onTap: () {
              showDialog(
                  context: context,
                  builder: (context) => AlertDialog(
                    title: const Text("Gemini Summary"),
                    content: Text(gemini_summ),
                    actions: [
                      TextButton(
                          onPressed: () {
                            Navigator.of(context).pop();
                          },
                          child: const Text("close"))
                    ],
                  )
              );
            },
            child: Container(
              decoration: const BoxDecoration(border: Border(bottom: BorderSide(color: Colors.black))),
                alignment: Alignment.center,
                child: Text(name)
            ),
          ),
        ),
        Expanded(
          child: Container(
            decoration: const BoxDecoration(border: Border(bottom: BorderSide(color: Colors.black))),
            alignment: Alignment.center,
            child: Text(company)
          ),
        ),
        Expanded(
          child: Container(
              decoration: const BoxDecoration(border: Border(bottom: BorderSide(color: Colors.black))),
              alignment: Alignment.center,
              child: Text(job_title)
          ),
        ),
        Expanded(
          child: Container(
              decoration: const BoxDecoration(border: Border(bottom: BorderSide(color: Colors.black))),
              alignment: Alignment.center,
              child: Text(location)
          ),
        ),
      ],
    );
  }
}
