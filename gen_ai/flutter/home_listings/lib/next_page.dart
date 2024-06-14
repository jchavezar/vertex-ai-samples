import 'package:flutter/material.dart';

class NextPage extends StatefulWidget {
  final String ? imageUri_1;
  final String ? imageUri_2;
  final String ? imageUri_3;
  final String ? imageUri_4;
  final String ? imageUri_5;
  final String ? imageUri_6;
  final String ? imageUri_7;
  final String ? imageUri_8;
  final String ? imageUri_9;
  final String ? imageUri_10;
  final String ? title;
  final int ? pricePerNight;
  final int ? guests;
  final amenities;
  final nearbyNeigh;
  final String ? description;

  const NextPage({
    super.key,
    this.imageUri_1,
    this.imageUri_2,
    this.imageUri_3,
    this.imageUri_4,
    this.imageUri_5,
    this.imageUri_6,
    this.imageUri_7,
    this.imageUri_8,
    this.imageUri_9,
    this.imageUri_10,
    this.title,
    this.pricePerNight,
    this.guests,
    this.amenities,
    this.nearbyNeigh,
    this.description,
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
              height: windowSize*0.050,
              child: Row(
                children: [
                  const Text(
                    "Photos Listing and Metadata Powered by: ",
                    style: TextStyle(fontSize: 28.0, fontWeight: FontWeight.bold),
                  ),
                  Padding(
                      padding: const EdgeInsets.all(2.0),
                      child: Image.network("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Google_Gemini_logo.svg/2560px-Google_Gemini_logo.svg.png")),
                ],
              )
          ),
          const SizedBox(height: 10.0),
          Row(
            children: [
              Container(
                  padding: const EdgeInsets.all(10.0),
                  margin: const EdgeInsets.only(top: 15.0, right: 10.0, left: 30.0,),
                  height: windowSize*0.32,
                  width: windowSize*0.8*0.80,
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Flexible(
                          flex: 50,
                          child: Container(
                            decoration: const BoxDecoration(
                                borderRadius: BorderRadius.only(topLeft: Radius.circular(12.0), bottomLeft: Radius.circular(12.0))
                            ),
                            child: ClipRRect(
                              borderRadius: const BorderRadius.only(
                                topLeft: Radius.circular(11.0),
                                bottomLeft: Radius.circular(11.0),
                              ),
                              child: Image.network("${widget.imageUri_1}",
                                  fit: BoxFit.fill,
                              ),
                            ),
                          )
                      ),
                      const SizedBox(width: 10),
                      Flexible(
                          flex: 25,
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Image.network(
                                "${widget.imageUri_2}",
                                  fit: BoxFit.fill,
                                height: 225,
                              ),
                              const SizedBox(height: 5),
                              Image.network("${widget.imageUri_3}",
                                  fit: BoxFit.fill,
                                height: 225,
                              ),
                            ],
                          )
                      ),
                      const SizedBox(width: 10),
                      Flexible(
                          flex: 25,
                          child: Container(
                            decoration: const BoxDecoration(
                                borderRadius: BorderRadius.only(topRight: Radius.circular(12.0), bottomRight: Radius.circular(12.0))
                            ),
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                ClipRRect(
                                  borderRadius: const BorderRadius.only(topRight: Radius.circular(11.0)),
                                  child: Image.network("${widget.imageUri_4}",
                                      fit: BoxFit.fill,
                                    height: 226,
                                  ),
                                ),
                                const SizedBox(height: 5),
                                ClipRRect(
                                  borderRadius: const BorderRadius.only(bottomRight: Radius.circular(11.0)),
                                  child: Image.network("${widget.imageUri_5}",
                                      fit: BoxFit.fill,
                                    height: 225,
                                  ),
                                ),
                              ],
                            ),
                          )
                      ),
                    ],
                  )
              ),
              Container(
                width: windowSize*0.8*0.35,
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
                    Text("${widget.description}", style: const TextStyle(fontSize: 16.0,)),
                    const SizedBox(height:12),
                    const Text("Title", style: TextStyle(fontSize: 18.0, fontWeight: FontWeight.bold),),
                    Text("${widget.title}", style: const TextStyle(fontSize: 16.0,)),
                    const SizedBox(height:12),
                    const Text("Price", style: TextStyle(fontSize: 18.0, fontWeight: FontWeight.bold),),
                    Text("${widget.pricePerNight}", style: const TextStyle(fontSize: 16.0,)),
                    const SizedBox(height:12),
                    const Text("Maximum Guests Number", style: TextStyle(fontSize: 18.0, fontWeight: FontWeight.bold),),
                    Text("${widget.guests}", style: const TextStyle(fontSize: 16.0,)),
                    const SizedBox(height:12),
                    const Text("Amenities", style: TextStyle(fontSize: 18.0, fontWeight: FontWeight.bold),),
                    Wrap(
                      spacing: 8.0,
                      children: widget.amenities.replaceAll(RegExp(r"[\[\]']"), '').trim().split('  ').map<Widget>((amenity) => // Specify the type
                      Text(amenity.trim(), style: const TextStyle(fontSize: 16.0))
                      ).toList(), // Convert to List<Widget>
                    ),
                    const SizedBox(height:12),
                    const Text("Neighbourhood", style: TextStyle(fontSize: 18.0, fontWeight: FontWeight.bold),),
                    Wrap(
                      spacing: 8.0,
                      children: widget.nearbyNeigh.replaceAll(RegExp(r"[\[\]']"), '').trim().split('  ').map<Widget>((nearbyNeighbourhood) => // Specify the type
                      Text(nearbyNeighbourhood.trim(), style: const TextStyle(fontSize: 16.0))
                      ).toList(), // Convert to List<Widget>
                    ),
                  ],
                ),
              )
            ],
          ),
          Row(
            children: [
              Container(
                  padding: const EdgeInsets.all(12.0),
                  margin: const EdgeInsets.only(left: 25.0, right: 25.0, top: 15.0),
                  height: windowSize*0.32,
                  width: windowSize*0.8*0.8,
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Flexible(
                          flex: 50,
                          child: Container(
                            decoration: const BoxDecoration(
                                borderRadius: BorderRadius.only(topLeft: Radius.circular(12.0), bottomLeft: Radius.circular(12.0))
                            ),
                            child: ClipRRect(
                              borderRadius: const BorderRadius.only(
                                topLeft: Radius.circular(11.0),
                                bottomLeft: Radius.circular(11.0),
                              ),
                              child: Image.network("${widget.imageUri_6}",
                                  fit: BoxFit.fill
                              ),
                            ),
                          )
                      ),
                      const SizedBox(width: 10),
                      Flexible(
                          flex: 25,
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Image.network("${widget.imageUri_7}",
                                  fit: BoxFit.fill,
                                height: 225,
                              ),
                              const SizedBox(height: 5),
                              Image.network("${widget.imageUri_8}",
                                  fit: BoxFit.fill,
                                height: 225,
                              ),
                            ],
                          )
                      ),
                      const SizedBox(width: 10),
                      Flexible(
                          flex: 25,
                          child: Container(
                            decoration: const BoxDecoration(
                                borderRadius: BorderRadius.only(topRight: Radius.circular(12.0), bottomRight: Radius.circular(12.0))
                            ),
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                ClipRRect(
                                  borderRadius: const BorderRadius.only(topRight: Radius.circular(11.0)),
                                  child: Image.network("${widget.imageUri_9}",
                                      fit: BoxFit.fill,
                                    height: 225,
                                  ),
                                ),
                                const SizedBox(height: 5),
                                ClipRRect(
                                  borderRadius: const BorderRadius.only(bottomRight: Radius.circular(11.0)),
                                  child: Image.network("${widget.imageUri_10}",
                                      fit: BoxFit.fill,
                                    height: 225,
                                  ),
                                ),
                              ],
                            ),
                          )
                      ),
                    ],
                  )
              ),
              const SizedBox(width: 200,)
            ],
          ),
          const SizedBox(height: 10.0),
        ],
      ),
    );
  }
}
